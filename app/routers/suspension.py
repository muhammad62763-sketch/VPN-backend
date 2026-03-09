"""Account suspension management endpoints (Admin only)"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from app.services import db, security_service
from app.routers.admin import require_admin

router = APIRouter()

class SuspendUserRequest(BaseModel):
    reason: str
    duration_days: Optional[int] = None  # None = permanent

@router.post("/users/{user_id}/suspend", status_code=200)
async def suspend_user(
    user_id: str,
    body: SuspendUserRequest,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Suspend user account"""
    pool = await db.get_pool()
    
    # Check if user exists
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate suspension end date
    suspended_until = None
    if body.duration_days:
        from datetime import timedelta
        suspended_until = datetime.now(timezone.utc) + timedelta(days=body.duration_days)
    
    # Suspend user
    await pool.execute(
        """UPDATE users 
           SET is_active = FALSE,
               suspension_reason = $1,
               suspended_at = NOW(),
               suspended_by = $2
           WHERE id = $3""",
        body.reason, admin["sub"], user_id
    )
    
    # Revoke all sessions
    await db.revoke_all_user_tokens(user_id)
    await security_service.revoke_all_user_sessions(user_id)
    
    # Log audit
    await db.log_audit(
        actor_id=admin["sub"],
        action="suspend_user",
        target_id=user_id,
        metadata={
            "reason": body.reason,
            "duration_days": body.duration_days,
            "suspended_until": suspended_until.isoformat() if suspended_until else "permanent"
        },
        ip_address=request.client.host
    )
    
    # Send notification to user
    from app.routers.notifications import create_notification
    await create_notification(
        user_id,
        "Account Suspended",
        f"Your account has been suspended. Reason: {body.reason}",
        "error"
    )
    
    return {
        "message": "User suspended",
        "reason": body.reason,
        "suspended_until": suspended_until.isoformat() if suspended_until else "permanent"
    }

@router.post("/users/{user_id}/unsuspend", status_code=200)
async def unsuspend_user(
    user_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Unsuspend user account"""
    pool = await db.get_pool()
    
    # Check if user exists
    user = await db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Unsuspend user
    await pool.execute(
        """UPDATE users 
           SET is_active = TRUE,
               suspension_reason = NULL,
               suspended_at = NULL,
               suspended_by = NULL
           WHERE id = $1""",
        user_id
    )
    
    # Log audit
    await db.log_audit(
        actor_id=admin["sub"],
        action="unsuspend_user",
        target_id=user_id,
        ip_address=request.client.host
    )
    
    # Send notification to user
    from app.routers.notifications import create_notification
    await create_notification(
        user_id,
        "Account Reactivated",
        "Your account has been reactivated. You can now log in.",
        "success"
    )
    
    return {"message": "User unsuspended"}

@router.get("/users/{user_id}/suspension-info", status_code=200)
async def get_suspension_info(
    user_id: str,
    admin: dict = Depends(require_admin)
):
    """Get suspension information for user"""
    pool = await db.get_pool()
    
    user = await pool.fetchrow(
        """SELECT suspension_reason, suspended_at, suspended_by, is_active
           FROM users WHERE id = $1""",
        user_id
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get admin who suspended
    suspended_by_email = None
    if user["suspended_by"]:
        admin_user = await db.get_user_by_id(str(user["suspended_by"]))
        if admin_user:
            suspended_by_email = admin_user["email"]
    
    return {
        "is_suspended": not user["is_active"],
        "suspension_reason": user["suspension_reason"],
        "suspended_at": user["suspended_at"].isoformat() if user["suspended_at"] else None,
        "suspended_by": suspended_by_email
    }
