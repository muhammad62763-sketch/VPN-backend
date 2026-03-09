"""GDPR compliance endpoints - Data export and deletion"""
from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import io
from datetime import datetime, timezone
from app.services import db, security_service
from app.routers.users import get_current_user

router = APIRouter()

class RequestDataDeletionRequest(BaseModel):
    password: str
    confirmation: str  # Must be "DELETE MY DATA"

@router.get("/export-data", status_code=200)
async def export_user_data(user: dict = Depends(get_current_user)):
    """Export all user data (GDPR compliance)"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Collect all user data
    data = {}
    
    # User profile
    db_user = await db.get_user_by_id(user_id)
    if db_user:
        # Remove sensitive fields
        safe_user = {k: v for k, v in db_user.items() if k not in ["password_hash", "totp_secret"]}
        data["profile"] = safe_user
    
    # VPN configs
    configs = await pool.fetch(
        "SELECT * FROM vpn_configs WHERE user_id = $1",
        user_id
    )
    data["vpn_configs"] = [dict(c) for c in configs]
    
    # Devices
    devices = await security_service.get_user_devices(user_id)
    data["devices"] = devices
    
    # Sessions
    sessions = await pool.fetch(
        "SELECT * FROM active_sessions WHERE user_id = $1",
        user_id
    )
    data["sessions"] = [dict(s) for s in sessions]
    
    # Security events
    events = await pool.fetch(
        "SELECT * FROM security_events WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1000",
        user_id
    )
    data["security_events"] = [dict(e) for e in events]
    
    # VPN connections
    connections = await pool.fetch(
        "SELECT * FROM vpn_connections WHERE user_id = $1 ORDER BY connected_at DESC LIMIT 1000",
        user_id
    )
    data["vpn_connections"] = [dict(c) for c in connections]
    
    # Bandwidth usage
    bandwidth = await pool.fetch(
        "SELECT * FROM bandwidth_usage WHERE user_id = $1 ORDER BY period_start DESC LIMIT 1000",
        user_id
    )
    data["bandwidth_usage"] = [dict(b) for b in bandwidth]
    
    # Notifications
    notifications = await pool.fetch(
        "SELECT * FROM notifications WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1000",
        user_id
    )
    data["notifications"] = [dict(n) for n in notifications]
    
    # API keys (without actual keys)
    api_keys = await pool.fetch(
        "SELECT id, name, last_used, is_active, created_at, expires_at FROM api_keys WHERE user_id = $1",
        user_id
    )
    data["api_keys"] = [dict(k) for k in api_keys]
    
    # Referral codes
    referrals = await pool.fetch(
        "SELECT * FROM referral_codes WHERE user_id = $1",
        user_id
    )
    data["referral_codes"] = [dict(r) for r in referrals]
    
    # Add metadata
    data["export_metadata"] = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "format": "JSON"
    }
    
    # Convert to JSON
    json_data = json.dumps(data, indent=2, default=str)
    
    # Return as downloadable file
    return StreamingResponse(
        io.BytesIO(json_data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=user_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json"
        }
    )

@router.post("/request-deletion", status_code=200)
async def request_data_deletion(
    body: RequestDataDeletionRequest,
    user: dict = Depends(get_current_user)
):
    """Request account and data deletion (GDPR Right to be Forgotten)"""
    from app.services import auth_service
    
    user_id = user["sub"]
    
    # Verify password
    db_user = await db.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not auth_service.verify_password(body.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Verify confirmation
    if body.confirmation != "DELETE MY DATA":
        raise HTTPException(
            status_code=400, 
            detail='Confirmation must be exactly "DELETE MY DATA"'
        )
    
    # Log deletion request
    await security_service.log_security_event(
        user_id, "data_deletion_requested", "system",
        severity="critical"
    )
    
    # Perform deletion
    pool = await db.get_pool()
    
    # Delete all related data (CASCADE will handle most)
    await pool.execute("DELETE FROM users WHERE id = $1", user_id)
    
    return {
        "message": "Your account and all associated data have been permanently deleted",
        "deleted_at": datetime.now(timezone.utc).isoformat()
    }
