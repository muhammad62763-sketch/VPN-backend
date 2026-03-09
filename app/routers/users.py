from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, EmailStr
from app.services import auth_service, db, security_service

router = APIRouter()

# ── Auth Dependency ───────────────────────────────────────────────────────────
async def get_current_user(authorization: str = Header(...), x_device_id: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.removeprefix("Bearer ")
    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not auth_service.verify_device_binding(payload, x_device_id):
        raise HTTPException(status_code=401, detail="Device mismatch")
    
    # Check if session is still valid
    jti = payload.get("jti")
    if jti and not await security_service.is_session_valid(jti):
        raise HTTPException(status_code=401, detail="Session expired or revoked")
    
    return payload

# ── Request Schemas ───────────────────────────────────────────────────────────
class UpdateProfileRequest(BaseModel):
    email: EmailStr | None = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# ── Get Own Profile ───────────────────────────────────────────────────────────
@router.get("/me")
async def get_profile(user: dict = Depends(get_current_user)):
    """Return the authenticated user's own profile."""
    db_user = await db.get_user_by_id(user["sub"])
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    # Never return password_hash
    return {
        "id":               str(db_user["id"]),
        "email":            db_user["email"],
        "role":             db_user["role"],
        "is_active":        db_user["is_active"],
        "bandwidth_limit":  db_user["bandwidth_limit"],
        "created_at":       db_user["created_at"].isoformat(),
    }

# ── Update Own Profile ────────────────────────────────────────────────────────
@router.patch("/me")
async def update_profile(
    body: UpdateProfileRequest,
    user: dict = Depends(get_current_user),
):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "email" in updates:
        existing = await db.get_user_by_email(updates["email"])
        if existing and str(existing["id"]) != user["sub"]:
            raise HTTPException(status_code=409, detail="Email already in use")
    updated = await db.update_user(user["sub"], **updates)
    return {"message": "Profile updated", "email": updated.get("email")}

# ── Change Password ───────────────────────────────────────────────────────────
@router.post("/me/change-password", status_code=204)
async def change_password(
    body: ChangePasswordRequest,
    request: Request,
    user: dict = Depends(get_current_user),
):
    from app.utils.password_strength import check_password_strength
    
    user_id = user["sub"]
    db_user = await db.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not auth_service.verify_password(body.current_password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password incorrect")
    
    # Check new password strength
    is_valid, message, score = check_password_strength(body.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Password too weak: {message}")
    
    new_hash = auth_service.hash_password(body.new_password)
    
    # Update password and last_password_change timestamp
    pool = await db.get_pool()
    await pool.execute(
        "UPDATE users SET password_hash = $1, last_password_change = NOW() WHERE id = $2",
        new_hash, user_id
    )
    
    # Revoke all sessions — forces re-login on all devices
    await db.revoke_all_user_tokens(user_id)
    await security_service.revoke_all_user_sessions(user_id)
    
    # Log security event
    await security_service.log_security_event(
        user_id, "password_change", request.client.host,
        request.headers.get("user-agent"), user.get("device"),
        severity="info"
    )

# ── Get Own VPN Configs ───────────────────────────────────────────────────────
@router.get("/me/configs")
async def get_my_configs(user: dict = Depends(get_current_user)):
    """Return all VPN configs belonging to the authenticated user."""
    pool = await db.get_pool()
    rows = await pool.fetch(
        "SELECT config_id, client_ip, is_revoked, created_at "
        "FROM vpn_configs WHERE user_id = $1 ORDER BY created_at DESC",
        user["sub"]
    )
    return {"configs": [dict(r) for r in rows]}

# ── Delete Own Account ────────────────────────────────────────────────────────
@router.delete("/me", status_code=204)
async def delete_account(
    request: Request,
    user: dict = Depends(get_current_user),
):
    """User self-deletes their account and all associated data."""
    user_id = user["sub"]
    
    # Log before deletion
    await security_service.log_security_event(
        user_id, "account_deleted", request.client.host,
        request.headers.get("user-agent"), user.get("device"),
        severity="warning"
    )
    
    await db.revoke_all_user_tokens(user_id)
    await security_service.revoke_all_user_sessions(user_id)
    await db.release_ip(user_id)
    await db.delete_user(user_id)

# ── Get User Devices ──────────────────────────────────────────────────────────
@router.get("/me/devices")
async def get_devices(user: dict = Depends(get_current_user)):
    """Get all devices associated with the user account"""
    devices = await security_service.get_user_devices(user["sub"])
    return {"devices": devices}

# ── Get Security Summary ──────────────────────────────────────────────────────
@router.get("/me/security")
async def get_security_summary(user: dict = Depends(get_current_user)):
    """Get security summary for the user"""
    summary = await security_service.get_security_summary(user["sub"])
    return summary

# ── Get Security Events ───────────────────────────────────────────────────────
@router.get("/me/security-events")
async def get_security_events(
    limit: int = 50,
    user: dict = Depends(get_current_user)
):
    """Get recent security events for the user"""
    pool = await db.get_pool()
    events = await pool.fetch(
        """SELECT event_type, ip_address, user_agent, device_id, metadata, severity, created_at
           FROM security_events 
           WHERE user_id = $1 
           ORDER BY created_at DESC 
           LIMIT $2""",
        user["sub"], limit
    )
    return {"events": [dict(e) for e in events]}

# ── Get Active Sessions ───────────────────────────────────────────────────────
@router.get("/me/sessions")
async def get_active_sessions(user: dict = Depends(get_current_user)):
    """Get all active sessions for the user"""
    pool = await db.get_pool()
    sessions = await pool.fetch(
        """SELECT id, device_id, ip_address, user_agent, created_at, expires_at, last_activity
           FROM active_sessions 
           WHERE user_id = $1 AND expires_at > NOW()
           ORDER BY last_activity DESC""",
        user["sub"]
    )
    return {"sessions": [dict(s) for s in sessions]}

# ── Revoke Specific Session ───────────────────────────────────────────────────
@router.delete("/me/sessions/{session_id}", status_code=204)
async def revoke_session(
    session_id: str,
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Revoke a specific session"""
    pool = await db.get_pool()
    
    # Verify session belongs to user
    session = await pool.fetchrow(
        "SELECT jti FROM active_sessions WHERE id = $1 AND user_id = $2",
        session_id, user["sub"]
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await security_service.revoke_session(session["jti"])
    
    await security_service.log_security_event(
        user["sub"], "session_revoked", request.client.host,
        request.headers.get("user-agent"), user.get("device"),
        {"session_id": session_id}
    )
