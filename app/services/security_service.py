"""Enhanced security service for monitoring and protection"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import hashlib
from app.services import db

async def log_security_event(
    user_id: Optional[str],
    event_type: str,
    ip_address: str,
    user_agent: Optional[str] = None,
    device_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    severity: str = "info"
):
    """Log security-related events"""
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO security_events 
           (user_id, event_type, ip_address, user_agent, device_id, metadata, severity)
           VALUES ($1, $2, $3, $4, $5, $6, $7)""",
        user_id, event_type, ip_address, user_agent, device_id,
        metadata, severity
    )

async def check_failed_login_attempts(user_id: str) -> tuple[bool, Optional[int]]:
    """Check if user has too many failed login attempts"""
    pool = await db.get_pool()
    user = await pool.fetchrow(
        "SELECT failed_login_attempts, locked_until FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        return False, None
    
    # Check if account is locked
    if user['locked_until'] and user['locked_until'] > datetime.now(timezone.utc):
        remaining = int((user['locked_until'] - datetime.now(timezone.utc)).total_seconds())
        return True, remaining
    
    # Reset lock if expired
    if user['locked_until'] and user['locked_until'] <= datetime.now(timezone.utc):
        await pool.execute(
            "UPDATE users SET failed_login_attempts = 0, locked_until = NULL WHERE id = $1",
            user_id
        )
        return False, None
    
    return False, None

async def increment_failed_login(user_id: str, max_attempts: int = 5):
    """Increment failed login counter and lock if needed"""
    pool = await db.get_pool()
    result = await pool.fetchrow(
        """UPDATE users 
           SET failed_login_attempts = failed_login_attempts + 1
           WHERE id = $1
           RETURNING failed_login_attempts""",
        user_id
    )
    
    if result and result['failed_login_attempts'] >= max_attempts:
        # Lock account for 15 minutes
        lock_until = datetime.now(timezone.utc) + timedelta(minutes=15)
        await pool.execute(
            "UPDATE users SET locked_until = $1 WHERE id = $2",
            lock_until, user_id
        )

async def reset_failed_login(user_id: str):
    """Reset failed login counter on successful login"""
    pool = await db.get_pool()
    await pool.execute(
        """UPDATE users 
           SET failed_login_attempts = 0, locked_until = NULL, last_login = NOW()
           WHERE id = $1""",
        user_id
    )

async def create_session(
    user_id: str,
    device_id: str,
    jti: str,
    ip_address: str,
    user_agent: str,
    expires_at: datetime
):
    """Create active session for tracking"""
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO active_sessions 
           (user_id, device_id, jti, ip_address, user_agent, expires_at)
           VALUES ($1, $2, $3, $4, $5, $6)""",
        user_id, device_id, jti, ip_address, user_agent, expires_at
    )

async def revoke_session(jti: str):
    """Revoke a specific session"""
    pool = await db.get_pool()
    await pool.execute("DELETE FROM active_sessions WHERE jti = $1", jti)

async def revoke_all_user_sessions(user_id: str):
    """Revoke all sessions for a user"""
    pool = await db.get_pool()
    await pool.execute("DELETE FROM active_sessions WHERE user_id = $1", user_id)

async def is_session_valid(jti: str) -> bool:
    """Check if session is still valid"""
    pool = await db.get_pool()
    result = await pool.fetchrow(
        "SELECT id FROM active_sessions WHERE jti = $1 AND expires_at > NOW()",
        jti
    )
    return result is not None

async def track_device(
    user_id: str,
    device_id: str,
    device_name: Optional[str],
    device_type: Optional[str],
    ip_address: str
):
    """Track user device"""
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO user_devices 
           (user_id, device_id, device_name, device_type, last_ip, last_seen)
           VALUES ($1, $2, $3, $4, $5, NOW())
           ON CONFLICT (user_id, device_id) 
           DO UPDATE SET last_ip = $5, last_seen = NOW()""",
        user_id, device_id, device_name, device_type, ip_address
    )

async def get_user_devices(user_id: str) -> list[dict]:
    """Get all devices for a user"""
    pool = await db.get_pool()
    rows = await pool.fetch(
        """SELECT device_id, device_name, device_type, last_ip, last_seen, is_trusted
           FROM user_devices WHERE user_id = $1 ORDER BY last_seen DESC""",
        user_id
    )
    return [dict(r) for r in rows]

async def check_suspicious_activity(user_id: str, ip_address: str) -> bool:
    """Check for suspicious login patterns"""
    pool = await db.get_pool()
    
    # Check if login from new location
    recent_ips = await pool.fetch(
        """SELECT DISTINCT ip_address FROM security_events 
           WHERE user_id = $1 AND event_type = 'login' 
           AND created_at > NOW() - INTERVAL '30 days'
           LIMIT 10""",
        user_id
    )
    
    known_ips = [row['ip_address'] for row in recent_ips]
    
    # If IP is new and user has history, flag as suspicious
    if known_ips and ip_address not in known_ips:
        return True
    
    return False

async def log_vpn_connection(
    user_id: str,
    config_id: str,
    server_id: str,
    ip_address: str
):
    """Log VPN connection"""
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO vpn_connections 
           (user_id, config_id, server_id, ip_address)
           VALUES ($1, $2, $3, $4)""",
        user_id, config_id, server_id, ip_address
    )

async def get_connection_stats(user_id: str) -> dict:
    """Get user's VPN connection statistics"""
    pool = await db.get_pool()
    stats = await pool.fetchrow(
        """SELECT 
           COUNT(*) as total_connections,
           SUM(bytes_sent) as total_sent,
           SUM(bytes_received) as total_received,
           AVG(duration_seconds) as avg_duration
           FROM vpn_connections WHERE user_id = $1""",
        user_id
    )
    return dict(stats) if stats else {}

async def cleanup_expired_data():
    """Cleanup expired sessions and old data"""
    pool = await db.get_pool()
    
    # Delete expired sessions
    await pool.execute("DELETE FROM active_sessions WHERE expires_at < NOW()")
    
    # Delete old rate limit violations (older than 7 days)
    await pool.execute(
        "DELETE FROM rate_limit_violations WHERE last_violation < NOW() - INTERVAL '7 days'"
    )
    
    # Delete old security events (older than 90 days, keep critical)
    await pool.execute(
        """DELETE FROM security_events 
           WHERE created_at < NOW() - INTERVAL '90 days' 
           AND severity != 'critical'"""
    )

async def get_security_summary(user_id: str) -> dict:
    """Get security summary for a user"""
    pool = await db.get_pool()
    
    # Count active sessions
    active_sessions = await pool.fetchval(
        "SELECT COUNT(*) FROM active_sessions WHERE user_id = $1 AND expires_at > NOW()",
        user_id
    )
    
    # Count devices
    device_count = await pool.fetchval(
        "SELECT COUNT(*) FROM user_devices WHERE user_id = $1",
        user_id
    )
    
    # Recent security events
    recent_events = await pool.fetchval(
        """SELECT COUNT(*) FROM security_events 
           WHERE user_id = $1 AND created_at > NOW() - INTERVAL '7 days'""",
        user_id
    )
    
    # Failed login attempts in last 24h
    failed_logins = await pool.fetchval(
        """SELECT COUNT(*) FROM security_events 
           WHERE user_id = $1 AND event_type = 'failed_login' 
           AND created_at > NOW() - INTERVAL '24 hours'""",
        user_id
    )
    
    return {
        "active_sessions": active_sessions,
        "registered_devices": device_count,
        "recent_events_7d": recent_events,
        "failed_logins_24h": failed_logins
    }
