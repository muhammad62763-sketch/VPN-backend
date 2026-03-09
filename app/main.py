from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.routers import (
    auth, vpn, users, health, admin, webhooks,
    email, notifications, twofa, apikeys, referrals,
    gdpr, bandwidth, ipwhitelist, suspension
)
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.config import settings
from app.tasks.scheduler import run_scheduler

# Background task reference
background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup
    print("🚀 Starting VPN Backend API v2.0.0")
    
    # Start background scheduler
    task = asyncio.create_task(run_scheduler())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    
    yield
    
    # Shutdown
    print("🛑 Shutting down VPN Backend API")
    for task in background_tasks:
        task.cancel()

app = FastAPI(
    title="VPN Backend API",
    version="2.0.0",
    description="Enterprise-grade VPN management API with advanced security features",
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
    openapi_url=None if settings.ENVIRONMENT == "production" else "/openapi.json",
    lifespan=lifespan,
)

# Add middleware in correct order (last added = first executed)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "PUT"],
    allow_headers=["Authorization", "Content-Type", "X-Device-ID", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
    max_age=3600,
)

# Add trusted host middleware in production only
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.vercel.app", "yourdomain.com", "*.yourdomain.com"]
    )

# Include routers
app.include_router(health.router,        prefix="/api/v1",                tags=["Health"])
app.include_router(auth.router,          prefix="/api/v1/auth",           tags=["Auth"])
app.include_router(email.router,         prefix="/api/v1/email",          tags=["Email"])
app.include_router(twofa.router,         prefix="/api/v1/2fa",            tags=["2FA"])
app.include_router(users.router,         prefix="/api/v1/users",          tags=["Users"])
app.include_router(notifications.router, prefix="/api/v1/notifications",  tags=["Notifications"])
app.include_router(apikeys.router,       prefix="/api/v1/api-keys",       tags=["API Keys"])
app.include_router(referrals.router,     prefix="/api/v1/referrals",      tags=["Referrals"])
app.include_router(bandwidth.router,     prefix="/api/v1/bandwidth",      tags=["Bandwidth"])
app.include_router(gdpr.router,          prefix="/api/v1/gdpr",           tags=["GDPR"])
app.include_router(vpn.router,           prefix="/api/v1/vpn",            tags=["VPN"])
app.include_router(admin.router,         prefix="/api/v1/admin",          tags=["Admin"])
app.include_router(suspension.router,    prefix="/api/v1/admin",          tags=["Admin - Suspension"])
app.include_router(ipwhitelist.router,   prefix="/api/v1/admin/whitelist", tags=["Admin - IP Whitelist"])
app.include_router(webhooks.router,      prefix="/api/v1/webhooks",       tags=["Webhooks"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "VPN Backend API",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else None
    }
