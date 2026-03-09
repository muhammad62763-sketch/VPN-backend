from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
from app.services import auth_service, db
from app.config import settings

router = APIRouter()

# ── Admin Auth Dependency ─────────────────────────────────────────────────────
def require_admin(authorization: str = Header(...), x_device_id: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.removeprefix("Bearer ")
    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    if not auth_service.is_admin(payload):
        raise HTTPException(status_code=403, detail="Admin access required")
    if not auth_service.verify_device_binding(payload, x_device_id):
        raise HTTPException(status_code=401, detail="Device mismatch")
    return payload

def require_superadmin(authorization: str = Header(...), x_device_id: str = Header(...)):
    payload = require_admin(authorization=authorization, x_device_id=x_device_id)
    if not auth_service.is_superadmin(payload):
        raise HTTPException(status_code=403, detail="Superadmin access required")
    return payload

# ── Request Schemas ───────────────────────────────────────────────────────────
class AdminRegisterRequest(BaseModel):
    email: str
    password: str
    device_id: str
    admin_secret: str      # Must match ADMIN_REGISTRATION_SECRET in .env
    role: str = "admin"    # "admin" or "superadmin"

class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    is_banned: Optional[bool] = None
    role: Optional[str] = None
    bandwidth_limit: Optional[int] = None   # bytes; None = unlimited

# ── Register Admin Account ────────────────────────────────────────────────────
@router.post("/register", status_code=201)
async def admin_register(body: AdminRegisterRequest):
    """Create an admin account using a secret key. No rate limit applied."""
    if body.admin_secret != settings.ADMIN_REGISTRATION_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
    if body.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=400, detail="Invalid role")

    existing = await db.get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    pw_hash = auth_service.hash_password(body.password)
    user = await db.create_user(body.email, pw_hash, body.device_id, role=body.role)
    return {"message": f"{body.role} created", "user_id": str(user["id"])}

# ── Dashboard Stats ───────────────────────────────────────────────────────────
@router.get("/dashboard")
async def dashboard(admin: dict = Depends(require_admin)):
    """High-level dashboard: total users, active configs, etc."""
    pool = await db.get_pool()
    total_users   = await pool.fetchval("SELECT COUNT(*) FROM users WHERE role = 'user'")
    active_users  = await pool.fetchval("SELECT COUNT(*) FROM users WHERE is_active = TRUE AND role = 'user'")
    banned_users  = await pool.fetchval("SELECT COUNT(*) FROM users WHERE is_banned = TRUE")
    total_configs = await pool.fetchval("SELECT COUNT(*) FROM vpn_configs")
    active_configs= await pool.fetchval("SELECT COUNT(*) FROM vpn_configs WHERE is_revoked = FALSE")
    return {
        "total_users":    total_users,
        "active_users":   active_users,
        "banned_users":   banned_users,
        "total_configs":  total_configs,
        "active_configs": active_configs,
    }

# ── User Management ───────────────────────────────────────────────────────────
@router.get("/users")
async def list_users(
    limit: int = 50,
    offset: int = 0,
    admin: dict = Depends(require_admin)
):
    """List all users with full details."""
    users = await db.get_all_users(limit=limit, offset=offset)
    return {"users": users, "count": len(users)}

@router.get("/users/{user_id}")
async def get_user(user_id: str, admin: dict = Depends(require_admin)):
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    body: UpdateUserRequest,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Update any user field — role, ban status, bandwidth limit."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Only superadmin can change roles
    if "role" in updates and not auth_service.is_superadmin(admin):
        raise HTTPException(status_code=403, detail="Only superadmin can change roles")

    updated = await db.update_user(user_id, **updates)
    await db.log_audit(
        actor_id=admin["sub"],
        action="update_user",
        target_id=user_id,
        metadata=updates,
        ip_address=request.client.host
    )
    return updated

@router.post("/users/{user_id}/ban")
async def ban_user(user_id: str, request: Request, admin: dict = Depends(require_admin)):
    """Ban a user and force logout all their devices."""
    await db.ban_user(user_id)
    await db.revoke_all_user_tokens(user_id)
    await db.log_audit(
        actor_id=admin["sub"],
        action="ban_user",
        target_id=user_id,
        ip_address=request.client.host
    )
    return {"message": "User banned and all sessions revoked"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    request: Request,
    admin: dict = Depends(require_superadmin)   # superadmin only
):
    """Permanently delete a user and all their data."""
    await db.revoke_all_user_tokens(user_id)
    await db.release_ip(user_id)
    await db.delete_user(user_id)
    await db.log_audit(
        actor_id=admin["sub"],
        action="delete_user",
        target_id=user_id,
        ip_address=request.client.host
    )
    return {"message": "User permanently deleted"}

@router.post("/users/{user_id}/force-logout")
async def force_logout(user_id: str, request: Request, admin: dict = Depends(require_admin)):
    """Revoke all refresh tokens for a user — forces re-login on all devices."""
    await db.revoke_all_user_tokens(user_id)
    from app.services import security_service
    await security_service.revoke_all_user_sessions(user_id)
    await db.log_audit(
        actor_id=admin["sub"],
        action="force_logout",
        target_id=user_id,
        ip_address=request.client.host
    )
    return {"message": "All sessions revoked"}

# ── Premium Management ────────────────────────────────────────────────────────
@router.post("/users/{user_id}/grant-premium", status_code=200)
async def grant_premium(
    user_id: str,
    days: int,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Grant premium access to user"""
    from datetime import datetime, timezone, timedelta
    
    pool = await db.get_pool()
    
    # Calculate premium expiration
    premium_until = datetime.now(timezone.utc) + timedelta(days=days)
    
    await pool.execute(
        """UPDATE users 
           SET is_premium = TRUE
           WHERE id = $1""",
        user_id
    )
    
    await db.log_audit(
        actor_id=admin["sub"],
        action="grant_premium",
        target_id=user_id,
        metadata={"days": days, "expires_at": premium_until.isoformat()},
        ip_address=request.client.host
    )
    
    # Send notification
    from app.routers.notifications import create_notification
    await create_notification(
        user_id,
        "Premium Access Granted",
        f"You have been granted premium access for {days} days!",
        "success"
    )
    
    return {"message": "Premium granted", "expires_at": premium_until.isoformat()}

@router.post("/users/{user_id}/revoke-premium", status_code=200)
async def revoke_premium(
    user_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Revoke premium access from user"""
    pool = await db.get_pool()
    
    await pool.execute(
        "UPDATE users SET is_premium = FALSE WHERE id = $1",
        user_id
    )
    
    await db.log_audit(
        actor_id=admin["sub"],
        action="revoke_premium",
        target_id=user_id,
        ip_address=request.client.host
    )
    
    # Send notification
    from app.routers.notifications import create_notification
    await create_notification(
        user_id,
        "Premium Access Revoked",
        "Your premium access has been revoked.",
        "warning"
    )
    
    return {"message": "Premium revoked"}

# ── VPN Config Management ─────────────────────────────────────────────────────
@router.get("/vpn/configs")
async def list_all_configs(
    limit: int = 100,
    offset: int = 0,
    admin: dict = Depends(require_admin)
):
    """List all VPN configs across all users."""
    configs = await db.get_all_vpn_configs(limit=limit, offset=offset)
    return {"configs": configs, "count": len(configs)}

@router.post("/vpn/configs/{config_id}/revoke")
async def revoke_config(
    config_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Force-revoke any VPN config."""
    await db.revoke_vpn_config(config_id)
    await db.log_audit(
        actor_id=admin["sub"],
        action="revoke_vpn_config",
        target_id=config_id,
        ip_address=request.client.host
    )
    return {"message": "Config revoked"}

# ── Audit Logs ────────────────────────────────────────────────────────────────
@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    admin: dict = Depends(require_superadmin)    # superadmin only
):
    """Full audit trail of all admin actions."""
    logs = await db.get_audit_logs(limit=limit, offset=offset)
    return {"logs": logs, "count": len(logs)}

# ── Security Events ───────────────────────────────────────────────────────────
@router.get("/security-events")
async def get_all_security_events(
    limit: int = 100,
    offset: int = 0,
    severity: str = None,
    admin: dict = Depends(require_admin)
):
    """Get all security events across all users"""
    pool = await db.get_pool()
    
    if severity:
        events = await pool.fetch(
            """SELECT * FROM security_events 
               WHERE severity = $1 
               ORDER BY created_at DESC 
               LIMIT $2 OFFSET $3""",
            severity, limit, offset
        )
    else:
        events = await pool.fetch(
            """SELECT * FROM security_events 
               ORDER BY created_at DESC 
               LIMIT $1 OFFSET $2""",
            limit, offset
        )
    
    return {"events": [dict(e) for e in events], "count": len(events)}

# ── VPN Server Management ─────────────────────────────────────────────────────
@router.post("/vpn/servers", status_code=201)
async def create_vpn_server(
    country: str,
    country_code: str,
    city: str,
    public_key: str,
    endpoint: str,
    is_premium: bool = False,
    request: Request = None,
    admin: dict = Depends(require_superadmin)
):
    """Create a new VPN server"""
    pool = await db.get_pool()
    server = await pool.fetchrow(
        """INSERT INTO vpn_servers 
           (country, country_code, city, public_key, endpoint, is_premium)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING *""",
        country, country_code, city, public_key, endpoint, is_premium
    )
    
    await db.log_audit(
        actor_id=admin["sub"],
        action="create_vpn_server",
        target_id=str(server["id"]),
        metadata={"country": country, "city": city},
        ip_address=request.client.host if request else None
    )
    
    return dict(server)

@router.patch("/vpn/servers/{server_id}")
async def update_vpn_server(
    server_id: str,
    is_active: bool = None,
    load_percent: int = None,
    is_premium: bool = None,
    request: Request = None,
    admin: dict = Depends(require_admin)
):
    """Update VPN server status"""
    pool = await db.get_pool()
    
    # SECURITY FIX: Use whitelist of allowed fields to prevent SQL injection
    allowed_fields = {
        'is_active': is_active,
        'load_percent': load_percent,
        'is_premium': is_premium
    }
    
    # Filter out None values and validate field names
    updates = []
    values = []
    param_count = 1
    update_metadata = {}
    
    for field_name, field_value in allowed_fields.items():
        if field_value is not None:
            updates.append(f"{field_name} = ${param_count}")
            values.append(field_value)
            update_metadata[field_name] = field_value
            param_count += 1
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Validate load_percent range
    if load_percent is not None and (load_percent < 0 or load_percent > 100):
        raise HTTPException(status_code=400, detail="load_percent must be between 0 and 100")
    
    values.append(server_id)
    query = f"UPDATE vpn_servers SET {', '.join(updates)} WHERE id = ${param_count} RETURNING *"  # nosec B608 - Whitelisted fields only
    
    server = await pool.fetchrow(query, *values)
    
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    await db.log_audit(
        actor_id=admin["sub"],
        action="update_vpn_server",
        target_id=server_id,
        metadata={"updates": update_metadata},
        ip_address=request.client.host if request else None
    )
    
    return dict(server)

@router.delete("/vpn/servers/{server_id}")
async def delete_vpn_server(
    server_id: str,
    request: Request,
    admin: dict = Depends(require_superadmin)
):
    """Delete a VPN server"""
    pool = await db.get_pool()
    result = await pool.execute(
        "DELETE FROM vpn_servers WHERE id = $1",
        server_id
    )
    
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Server not found")
    
    await db.log_audit(
        actor_id=admin["sub"],
        action="delete_vpn_server",
        target_id=server_id,
        ip_address=request.client.host
    )
    
    return {"message": "Server deleted"}

# ── System Statistics ─────────────────────────────────────────────────────────
@router.get("/stats/system")
async def get_system_stats(admin: dict = Depends(require_admin)):
    """Get comprehensive system statistics"""
    pool = await db.get_pool()
    
    # User stats
    total_users = await pool.fetchval("SELECT COUNT(*) FROM users WHERE role = 'user'")
    active_users = await pool.fetchval("SELECT COUNT(*) FROM users WHERE is_active = TRUE AND role = 'user'")
    premium_users = await pool.fetchval("SELECT COUNT(*) FROM users WHERE is_premium = TRUE")
    
    # VPN stats
    total_configs = await pool.fetchval("SELECT COUNT(*) FROM vpn_configs")
    active_configs = await pool.fetchval("SELECT COUNT(*) FROM vpn_configs WHERE is_revoked = FALSE")
    total_servers = await pool.fetchval("SELECT COUNT(*) FROM vpn_servers WHERE is_active = TRUE")
    
    # Connection stats
    total_connections = await pool.fetchval("SELECT COUNT(*) FROM vpn_connections")
    active_connections = await pool.fetchval(
        "SELECT COUNT(*) FROM vpn_connections WHERE disconnected_at IS NULL"
    )
    
    # Security stats
    failed_logins_24h = await pool.fetchval(
        """SELECT COUNT(*) FROM security_events 
           WHERE event_type = 'failed_login' 
           AND created_at > NOW() - INTERVAL '24 hours'"""
    )
    
    suspicious_events_24h = await pool.fetchval(
        """SELECT COUNT(*) FROM security_events 
           WHERE severity = 'warning' 
           AND created_at > NOW() - INTERVAL '24 hours'"""
    )
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "premium": premium_users
        },
        "vpn": {
            "total_configs": total_configs,
            "active_configs": active_configs,
            "total_servers": total_servers,
            "total_connections": total_connections,
            "active_connections": active_connections
        },
        "security": {
            "failed_logins_24h": failed_logins_24h,
            "suspicious_events_24h": suspicious_events_24h
        }
    }
