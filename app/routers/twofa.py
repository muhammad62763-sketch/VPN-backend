"""Two-Factor Authentication (2FA/TOTP) endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services import totp_service
from app.routers.users import get_current_user

router = APIRouter()

class Enable2FARequest(BaseModel):
    password: str

class Verify2FASetupRequest(BaseModel):
    code: str

class Verify2FARequest(BaseModel):
    code: str

class Disable2FARequest(BaseModel):
    password: str

@router.post("/enable", status_code=200)
async def enable_2fa(
    body: Enable2FARequest,
    user: dict = Depends(get_current_user)
):
    """Enable 2FA and get QR code"""
    from app.services import db, auth_service
    
    user_id = user["sub"]
    
    # Verify password
    db_user = await db.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not auth_service.verify_password(body.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Check if already enabled
    if db_user.get("totp_enabled"):
        raise HTTPException(status_code=400, detail="2FA already enabled")
    
    # Generate secret and QR code
    secret, qr_code, backup_codes = await totp_service.enable_2fa(user_id)
    
    return {
        "message": "2FA setup initiated. Scan QR code and verify with code from authenticator app",
        "qr_code": qr_code,
        "secret": secret,
        "backup_codes": backup_codes
    }

@router.post("/verify-setup", status_code=200)
async def verify_2fa_setup(
    body: Verify2FASetupRequest,
    user: dict = Depends(get_current_user)
):
    """Verify 2FA setup with first code"""
    user_id = user["sub"]
    
    success = await totp_service.confirm_2fa_setup(user_id, body.code)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid code")
    
    return {"message": "2FA enabled successfully"}

@router.post("/verify", status_code=200)
async def verify_2fa_code(
    body: Verify2FARequest,
    user: dict = Depends(get_current_user)
):
    """Verify 2FA code"""
    user_id = user["sub"]
    
    success = await totp_service.verify_2fa_code(user_id, body.code)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid code")
    
    return {"message": "Code verified"}

@router.post("/disable", status_code=200)
async def disable_2fa(
    body: Disable2FARequest,
    user: dict = Depends(get_current_user)
):
    """Disable 2FA"""
    from app.services import db, auth_service
    
    user_id = user["sub"]
    
    # Verify password
    db_user = await db.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not auth_service.verify_password(body.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    
    await totp_service.disable_2fa(user_id)
    
    return {"message": "2FA disabled successfully"}

@router.get("/status", status_code=200)
async def get_2fa_status(user: dict = Depends(get_current_user)):
    """Get 2FA status"""
    from app.services import db
    
    user_id = user["sub"]
    db_user = await db.get_user_by_id(user_id)
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "enabled": db_user.get("totp_enabled", False),
        "backup_codes_remaining": len(db_user.get("backup_codes", []))
    }
