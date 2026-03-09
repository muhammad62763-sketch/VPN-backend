# Routers package
from app.routers import (
    auth, vpn, users, health, admin, webhooks,
    email, notifications, twofa, apikeys, referrals,
    gdpr, bandwidth, ipwhitelist, suspension
)

__all__ = [
    "auth", "vpn", "users", "health", "admin", "webhooks",
    "email", "notifications", "twofa", "apikeys", "referrals",
    "gdpr", "bandwidth", "ipwhitelist", "suspension"
]
