import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.services.auth_service import decode_token, is_admin, is_superadmin

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: dict = defaultdict(list)
        self._failed_attempts: dict = defaultdict(list)  # Track failed auth attempts
        self._blocked_ips: dict = {}  # Temporarily blocked IPs

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = time.time()
        
        # Check if IP is temporarily blocked
        if ip in self._blocked_ips:
            if now < self._blocked_ips[ip]:
                remaining = int(self._blocked_ips[ip] - now)
                return JSONResponse(
                    {"detail": f"Too many failed attempts. Blocked for {remaining}s"},
                    status_code=429,
                    headers={"Retry-After": str(remaining)},
                )
            else:
                del self._blocked_ips[ip]
        
        # ── Superadmins bypass all rate limiting ──────────────────────────────
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            payload = decode_token(token)
            if payload and is_superadmin(payload):
                return await call_next(request)
        
        # ── Admins get higher limits ──────────────────────────────────────────
        if auth_header.startswith("Bearer "):
            token = auth_header.removeprefix("Bearer ")
            payload = decode_token(token)
            if payload and is_admin(payload):
                max_requests = self.max_requests * 5  # 5x limit for admins
            else:
                max_requests = self.max_requests
        else:
            max_requests = self.max_requests

        # ── Standard rate limit ───────────────────────────────────────────────
        window_start = now - self.window
        self._buckets[ip] = [t for t in self._buckets[ip] if t > window_start]

        if len(self._buckets[ip]) >= max_requests:
            return JSONResponse(
                {"detail": "Too many requests"},
                status_code=429,
                headers={"Retry-After": str(self.window)},
            )

        self._buckets[ip].append(now)
        response = await call_next(request)
        
        # Track failed authentication attempts
        if response.status_code == 401 and request.url.path.startswith("/api/v1/auth"):
            self._failed_attempts[ip].append(now)
            self._failed_attempts[ip] = [t for t in self._failed_attempts[ip] if t > now - 300]  # 5 min window
            
            # Block IP after 10 failed attempts in 5 minutes
            if len(self._failed_attempts[ip]) >= 10:
                self._blocked_ips[ip] = now + 900  # Block for 15 minutes
                return JSONResponse(
                    {"detail": "Too many failed login attempts. IP blocked for 15 minutes"},
                    status_code=429,
                    headers={"Retry-After": "900"},
                )
        
        return response
