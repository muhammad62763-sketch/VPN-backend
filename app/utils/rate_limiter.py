"""Advanced rate limiting utilities"""
import time
from collections import defaultdict
from typing import Dict, List, Tuple

class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        capacity: Maximum tokens in bucket
        refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, return True if successful"""
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """Get time to wait until tokens are available"""
        self._refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate

class SlidingWindowRateLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, key: str) -> Tuple[bool, int]:
        """
        Check if request is allowed
        Returns (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - self.window
        
        # Remove old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key]
            if req_time > window_start
        ]
        
        current_count = len(self._requests[key])
        
        if current_count < self.max_requests:
            self._requests[key].append(now)
            return True, self.max_requests - current_count - 1
        
        return False, 0
    
    def get_reset_time(self, key: str) -> float:
        """Get time until rate limit resets"""
        if key not in self._requests or not self._requests[key]:
            return 0.0
        
        oldest_request = min(self._requests[key])
        reset_time = oldest_request + self.window
        return max(0.0, reset_time - time.time())
