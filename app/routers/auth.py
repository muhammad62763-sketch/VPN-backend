import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Header, Request, status
from pydantic import BaseModel
from app.models.user import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.services import auth_service, db, security_service
from app.config import settings
from app.utils.password_strength import check_password_strength

router = APIRouter()

class PasswordStrengthRequest(BaseModel):
    password: str

@router.post("/check-password")
async def check_password(body: PasswordStrengthRequest):
    """Check password strength without creating an account"""
    is_valid, message, score = check_password_strength(body.password)
    
    return {
        "is_valid": is_valid,
        "message": message,
        "score": score,
        "strength": "weak" if score < 40 else "medium" if score < 70 else "strong"
    }

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, request: Request):
    # Enhanced validation with password strength check
    from app.utils.password_strength import check_password_strength
    is_valid, message, score = check_password_strength(body.password)
    
    if not is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Password too weak: {message}"
        )
    
    existing = await db.get_user_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    pw_hash = auth_service.hash_password(body.password)
    user = await db.create_user(body.email, pw_hash, body.device_id)
    user_id = str(user["id"])

    # Create tokens with role
    access_token = auth_service.create_access_token(user_id, body.device_id, user["role"])
    refresh_token = auth_service.create_refresh_token(user_id, body.device_id, user["role"])

    # Store hashed refresh token
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    await db.store_refresh_token(user["id"], token_hash)
    
    # Create session tracking
    payload = auth_service.decode_token(access_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    await security_service.create_session(
        user_id, body.device_id, payload["jti"],
        request.client.host, request.headers.get("user-agent", ""), expires_at
    )
    
    # Track device
    await security_service.track_device(
        user_id, body.device_id, None, None, request.client.host
    )
    
    # Log security event
    await security_service.log_security_event(
        user_id, "register", request.client.host,
        request.headers.get("user-agent"), body.device_id
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request):
    user = await db.get_user_by_email(body.email)
    
    # Check if user exists and password is correct
    if not user or not auth_service.verify_password(body.password, user["password_hash"]):
        # Log failed attempt
        if user:
            await security_service.increment_failed_login(str(user["id"]), settings.MAX_LOGIN_ATTEMPTS)
            await security_service.log_security_event(
                str(user["id"]), "failed_login", request.client.host,
                request.headers.get("user-agent"), body.device_id, severity="warning"
            )
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_id = str(user["id"])
    
    # Check if account is locked
    is_locked, remaining = await security_service.check_failed_login_attempts(user_id)
    if is_locked:
        raise HTTPException(
            status_code=423,
            detail=f"Account locked due to too many failed attempts. Try again in {remaining} seconds"
        )
    
    # Check if account is active
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Account suspended")
    
    # Check if account is banned
    if user.get("is_banned"):
        raise HTTPException(status_code=403, detail="Account banned")
    
    # Check for suspicious activity
    is_suspicious = await security_service.check_suspicious_activity(user_id, request.client.host)
    if is_suspicious:
        await security_service.log_security_event(
            user_id, "suspicious_login", request.client.host,
            request.headers.get("user-agent"), body.device_id,
            {"reason": "new_location"}, severity="warning"
        )

    # Create tokens with role
    access_token = auth_service.create_access_token(user_id, body.device_id, user["role"])
    refresh_token = auth_service.create_refresh_token(user_id, body.device_id, user["role"])

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    await db.store_refresh_token(user["id"], token_hash)
    
    # Create session tracking
    payload = auth_service.decode_token(access_token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    await security_service.create_session(
        user_id, body.device_id, payload["jti"],
        request.client.host, request.headers.get("user-agent", ""), expires_at
    )
    
    # Track device
    await security_service.track_device(
        user_id, body.device_id, None, None, request.client.host
    )
    
    # Reset failed login attempts
    await security_service.reset_failed_login(user_id)
    
    # Log successful login
    await security_service.log_security_event(
        user_id, "login", request.client.host,
        request.headers.get("user-agent"), body.device_id
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, request: Request, x_device_id: str = Header(...)):
    payload = auth_service.decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if not auth_service.verify_device_binding(payload, x_device_id):
        raise HTTPException(status_code=401, detail="Device mismatch")
    
    # Check if session is still valid
    jti = payload.get("jti")
    if jti and not await security_service.is_session_valid(jti):
        raise HTTPException(status_code=401, detail="Session expired or revoked")

    # Rotate: revoke old, issue new
    old_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    await db.revoke_refresh_token(old_hash)
    
    # Revoke old session
    if jti:
        await security_service.revoke_session(jti)

    user_id = str(payload["sub"])
    role = payload.get("role", "user")
    
    # Create new tokens
    new_access = auth_service.create_access_token(user_id, x_device_id, role)
    new_refresh = auth_service.create_refresh_token(user_id, x_device_id, role)

    new_hash = hashlib.sha256(new_refresh.encode()).hexdigest()
    await db.store_refresh_token(user_id, new_hash)
    
    # Create new session
    new_payload = auth_service.decode_token(new_access)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    await security_service.create_session(
        user_id, x_device_id, new_payload["jti"],
        request.client.host, request.headers.get("user-agent", ""), expires_at
    )

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest, request: Request):
    payload = auth_service.decode_token(body.refresh_token)
    
    # Revoke refresh token
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    await db.revoke_refresh_token(token_hash)
    
    # Revoke session if JTI exists
    if payload and payload.get("jti"):
        await security_service.revoke_session(payload["jti"])
    
    # Log logout event
    if payload:
        await security_service.log_security_event(
            payload["sub"], "logout", request.client.host,
            request.headers.get("user-agent"), payload.get("device")
        )
