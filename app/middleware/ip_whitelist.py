from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.config import settings

class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """Optional IP whitelist for admin endpoints"""
    async def dispatch(self, request: Request, call_next):
        # Only apply to admin endpoints
        if not request.url.path.startswith("/api/v1/admin"):
            return await call_next(request)
        
        # Check if IP whitelist is configured
        if not hasattr(settings, 'ADMIN_IP_WHITELIST') or not settings.ADMIN_IP_WHITELIST:
            return await call_next(request)
        
        client_ip = request.client.host
        
        # Allow if IP is in whitelist
        if client_ip in settings.ADMIN_IP_WHITELIST:
            return await call_next(request)
        
        return JSONResponse(
            {"detail": "Access denied from this IP address"},
            status_code=403
        )
