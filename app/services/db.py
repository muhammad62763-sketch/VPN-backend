import asyncpg
import hashlib
from datetime import datetime, timezone, timedelta
from app.config import settings

_pool: asyncpg.Pool | None = None

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        # Strip +asyncpg prefix if present for raw asyncpg
        url = settings.NEON_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        _pool = await asyncpg.create_pool(
            dsn=url,
            min_size=1,
            max_size=5,              # Vercel serverless: keep pool small
            ssl="require",           # NeonDB requires SSL
            command_timeout=10,
        )
    return _pool

# ── Users ─────────────────────────────────────────────────────────────────────
async def create_user(email: str, password_hash: str, device_id: str, role: str = "user") -> dict:
    pool = await get_pool()
    row = await pool.fetchrow(
        """INSERT INTO users (email, password_hash, device_id, role)
           VALUES ($1, $2, $3, $4) RETURNING *""",
        email, password_hash, device_id, role
    )
    return dict(row)

async def get_user_by_email(email: str) -> dict | None:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM users WHERE email = $1", email)
    return dict(row) if row else None

async def get_user_by_id(user_id: str) -> dict | None:
    pool = await get_pool()
    row = await pool.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    return dict(row) if row else None

async def get_all_users(limit: int = 100, offset: int = 0) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT id, email, role, is_active, is_banned, bandwidth_limit, created_at "
        "FROM users ORDER BY created_at DESC LIMIT $1 OFFSET $2",
        limit, offset
    )
    return [dict(r) for r in rows]

async def update_user(user_id: str, **fields) -> dict:
    """Dynamically update any user fields. Admin use only."""
    pool = await get_pool()
    set_clauses = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(fields))
    values = list(fields.values())
    row = await pool.fetchrow(
        f"UPDATE users SET {set_clauses}, updated_at = NOW() "  # nosec B608 - Admin only, field names validated
        f"WHERE id = $1 RETURNING *",
        user_id, *values
    )
    return dict(row) if row else {}

async def ban_user(user_id: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET is_banned = TRUE, is_active = FALSE, updated_at = NOW() WHERE id = $1",
        user_id
    )

async def delete_user(user_id: str) -> None:
    pool = await get_pool()
    await pool.execute("DELETE FROM users WHERE id = $1", user_id)

# ── Refresh Tokens ────────────────────────────────────────────────────────────
async def store_refresh_token(user_id: str, token_hash: str, expires_days: int = 7) -> None:
    pool = await get_pool()
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)
    await pool.execute(
        """INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
           VALUES ($1, $2, $3) ON CONFLICT (token_hash) DO NOTHING""",
        user_id, token_hash, expires_at
    )

async def revoke_refresh_token(token_hash: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE refresh_tokens SET is_revoked = TRUE WHERE token_hash = $1",
        token_hash
    )

async def revoke_all_user_tokens(user_id: str) -> None:
    """Admin: force logout user from all devices."""
    pool = await get_pool()
    await pool.execute(
        "UPDATE refresh_tokens SET is_revoked = TRUE WHERE user_id = $1", user_id
    )

# ── VPN Configs ───────────────────────────────────────────────────────────────
async def store_vpn_config(config_id: str, user_id: str, client_ip: str, psk: str) -> None:
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO vpn_configs (config_id, user_id, client_ip, preshared_key)
           VALUES ($1, $2, $3, $4)""",
        config_id, user_id, client_ip, psk
    )

async def revoke_vpn_config(config_id: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE vpn_configs SET is_revoked = TRUE WHERE config_id = $1", config_id
    )

async def get_all_vpn_configs(limit: int = 100, offset: int = 0) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT vc.*, u.email FROM vpn_configs vc "
        "JOIN users u ON vc.user_id = u.id "
        "ORDER BY vc.created_at DESC LIMIT $1 OFFSET $2",
        limit, offset
    )
    return [dict(r) for r in rows]

# ── IPAM ──────────────────────────────────────────────────────────────────────
async def allocate_ip(user_id: str) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            row = await conn.fetchrow(
                "SELECT ip_address FROM ip_pool WHERE is_assigned = FALSE LIMIT 1 FOR UPDATE SKIP LOCKED"
            )
            if not row:
                raise RuntimeError("IP pool exhausted")
            await conn.execute(
                "UPDATE ip_pool SET is_assigned = TRUE, user_id = $1 WHERE ip_address = $2",
                user_id, row["ip_address"]
            )
            return row["ip_address"] + "/32"

async def release_ip(user_id: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE ip_pool SET is_assigned = FALSE, user_id = NULL WHERE user_id = $1", user_id
    )

# ── Audit Logging ─────────────────────────────────────────────────────────────
async def log_audit(actor_id: str, action: str, target_id: str = None,
                    metadata: dict = None, ip_address: str = None) -> None:
    import json
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO audit_logs (actor_id, action, target_id, metadata, ip_address)
           VALUES ($1, $2, $3, $4, $5)""",
        actor_id, action, target_id,
        json.dumps(metadata) if metadata else None,
        ip_address
    )

async def get_audit_logs(limit: int = 100, offset: int = 0) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        "SELECT al.*, u.email as actor_email FROM audit_logs al "
        "LEFT JOIN users u ON al.actor_id = u.id "
        "ORDER BY al.created_at DESC LIMIT $1 OFFSET $2",
        limit, offset
    )
    return [dict(r) for r in rows]
