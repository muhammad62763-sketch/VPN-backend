"""Email verification and password reset endpoints"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from app.services import email_service, auth_service, db
from app.routers.users import get_current_user

router = APIRouter()

class RequestPasswordResetRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    token: str

@router.post("/send-verification", status_code=200)
async def send_verification_email(
    request: Request,
    user: dict = Depends(get_current_user)
):
    """Send email verification link to user"""
    user_id = user["sub"]
    
    # Get user email
    db_user = await db.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.get("email_verified"):
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Send verification email
    base_url = request.base_url.scheme + "://" + request.base_url.netloc
    await email_service.send_verification_email(user_id, db_user["email"], base_url)
    
    return {"message": "Verification email sent"}

@router.post("/verify-email", status_code=200)
async def verify_email(body: VerifyEmailRequest):
    """Verify email with token"""
    user_id = await email_service.verify_email_token(body.token)
    
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    return {"message": "Email verified successfully"}

@router.post("/request-password-reset", status_code=200)
async def request_password_reset(body: RequestPasswordResetRequest, request: Request):
    """Request password reset link"""
    user = await db.get_user_by_email(body.email)
    
    # Always return success to prevent email enumeration
    if user:
        base_url = request.base_url.scheme + "://" + request.base_url.netloc
        await email_service.send_password_reset_email(
            str(user["id"]), 
            user["email"], 
            base_url
        )
    
    return {"message": "If email exists, password reset link has been sent"}

@router.post("/reset-password", status_code=200)
async def reset_password(body: ResetPasswordRequest):
    """Reset password with token"""
    from app.utils.password_strength import check_password_strength
    
    # Verify token
    user_id = await email_service.verify_password_reset_token(body.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Check password strength
    is_valid, message, score = check_password_strength(body.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Password too weak: {message}")
    
    # Update password
    new_hash = auth_service.hash_password(body.new_password)
    pool = await db.get_pool()
    await pool.execute(
        "UPDATE users SET password_hash = $1, last_password_change = NOW() WHERE id = $2",
        new_hash, user_id
    )
    
    # Revoke all sessions
    await db.revoke_all_user_tokens(user_id)
    from app.services import security_service
    await security_service.revoke_all_user_sessions(user_id)
    
    return {"message": "Password reset successfully"}
