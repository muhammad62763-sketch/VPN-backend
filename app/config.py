from pydantic_settings import BaseSettings
from typing import List
import json

class Settings(BaseSettings):
    # ── NeonDB ────────────────────────────────────────────────────────────────
    NEON_DATABASE_URL: str

    # ── JWT ───────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Admin ─────────────────────────────────────────────────────────────────
    ADMIN_REGISTRATION_SECRET: str
    ADMIN_IP_WHITELIST: str = "[]"  # JSON array of allowed IPs for admin access

    # ── App ───────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: str = '["http://localhost:3000"]'
    ENVIRONMENT: str = "production"
    
    # ── Security ──────────────────────────────────────────────────────────────
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION: int = 900  # 15 minutes in seconds
    SESSION_TIMEOUT: int = 3600  # 1 hour
    REQUIRE_2FA_FOR_ADMIN: bool = True
    
    # ── VPN ───────────────────────────────────────────────────────────────────
    WG_SERVER_PUBLIC_KEY: str
    WG_SERVER_ENDPOINT: str
    WG_DNS: str = "1.1.1.1"
    MAX_DEVICES_PER_USER: int = 5
    DEFAULT_BANDWIDTH_LIMIT: int = 107374182400  # 100 GB

    # ── Signing ───────────────────────────────────────────────────────────────
    ED25519_PRIVATE_KEY_HEX: str
    
    # ── Monitoring ────────────────────────────────────────────────────────────
    ENABLE_METRICS: bool = True
    ENABLE_AUDIT_LOGGING: bool = True

    class Config:
        env_file = ".env"
    
    @property
    def origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS JSON string to list."""
        try:
            return json.loads(self.ALLOWED_ORIGINS)
        except:
            return ["http://localhost:3000"]
    
    @property
    def admin_ips(self) -> List[str]:
        """Parse ADMIN_IP_WHITELIST JSON string to list."""
        try:
            return json.loads(self.ADMIN_IP_WHITELIST)
        except:
            return []

settings = Settings()
