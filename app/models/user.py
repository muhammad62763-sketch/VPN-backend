from pydantic import BaseModel, EmailStr, field_validator
import re

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain digit")
        if not re.search(r"[!@#$%^&*]", v):
            raise ValueError("Must contain special character")
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_id: str
    totp_code: str | None = None     # TOTP MFA (optional but recommended)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int                  # seconds

class RefreshRequest(BaseModel):
    refresh_token: str
