from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt
import secrets
from app.config import settings

# Enhanced password hashing with higher cost factor
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=14)).decode()  # Increased from 12 to 14

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(user_id: str, device_id: str, role: str = "user") -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    # Add jti (JWT ID) for token revocation tracking
    jti = secrets.token_urlsafe(32)
    payload = {
        "sub": user_id,
        "device": device_id,
        "role": role,
        "type": "access",
        "jti": jti,  # Unique token identifier
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "iss": "vpn-backend",
        "aud": "vpn-client",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: str, device_id: str, role: str = "user") -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    jti = secrets.token_urlsafe(32)
    payload = {
        "sub": user_id,
        "device": device_id,
        "role": role,
        "type": "refresh",
        "jti": jti,
        "iat": datetime.now(timezone.utc),
        "exp": expire,
        "iss": "vpn-backend",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=["HS256"],
            audience="vpn-client",
            issuer="vpn-backend",
            options={
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
    except jwt.PyJWTError:
        return None

def verify_device_binding(payload: dict, device_id: str) -> bool:
    return payload.get("device") == device_id

def is_admin(payload: dict) -> bool:
    return payload.get("role") in ("admin", "superadmin")

def is_superadmin(payload: dict) -> bool:
    return payload.get("role") == "superadmin"

def generate_totp_secret() -> str:
    """Generate TOTP secret for 2FA"""
    return secrets.token_urlsafe(32)

def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes for 2FA recovery"""
    return [secrets.token_urlsafe(8) for _ in range(count)]
