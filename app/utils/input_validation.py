"""
Input validation utilities for security
Prevents injection attacks and validates data formats
"""
import re
import ipaddress
from typing import Optional
from uuid import UUID

def validate_uuid(value: str) -> bool:
    """Validate UUID format"""
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False

def validate_email(email: str) -> bool:
    """Validate email format (basic check)"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) and len(email) <= 254

def validate_device_id(device_id: str) -> bool:
    """Validate device ID format (alphanumeric, hyphens, underscores only)"""
    if not device_id or len(device_id) > 128:
        return False
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, device_id))

def validate_ip_address(ip: str) -> bool:
    """Validate IP address (IPv4 or IPv6)"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_country_code(code: str) -> bool:
    """Validate ISO 3166-1 alpha-2 country code"""
    if not code or len(code) != 2:
        return False
    return code.isalpha() and code.isupper()

def validate_config_id(config_id: str) -> bool:
    """Validate VPN config ID format"""
    if not config_id or len(config_id) > 64:
        return False
    # Allow alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, config_id))

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input - remove control characters"""
    if not value:
        return ""
    # Remove control characters except newline and tab
    sanitized = ''.join(char for char in value if char.isprintable() or char in '\n\t')
    return sanitized[:max_length]

def validate_port(port: int) -> bool:
    """Validate port number"""
    return 1 <= port <= 65535

def validate_bandwidth_limit(limit: Optional[int]) -> bool:
    """Validate bandwidth limit (bytes)"""
    if limit is None:
        return True  # None means unlimited
    return limit >= 0 and limit <= 10_995_116_277_760  # 10 TB max

def validate_jwt_token(token: str) -> bool:
    """Validate JWT token format (basic structure check)"""
    if not token:
        return False
    parts = token.split('.')
    if len(parts) != 3:
        return False
    # Each part should be base64url encoded
    pattern = r'^[A-Za-z0-9_-]+$'
    return all(re.match(pattern, part) for part in parts)

def validate_api_key_format(key: str) -> bool:
    """Validate API key format"""
    if not key or not key.startswith('vpn_'):
        return False
    if len(key) < 20 or len(key) > 128:
        return False
    pattern = r'^vpn_[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, key))

def validate_referral_code(code: str) -> bool:
    """Validate referral code format"""
    if not code or len(code) < 6 or len(code) > 32:
        return False
    pattern = r'^[A-Z0-9]+$'
    return bool(re.match(pattern, code))

def validate_totp_code(code: str) -> bool:
    """Validate TOTP code format (6 digits)"""
    if not code or len(code) != 6:
        return False
    return code.isdigit()

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url or len(url) > 2048:
        return False
    pattern = r'^https?://[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:/[^\s]*)?$'
    return bool(re.match(pattern, url))

def validate_wireguard_key(key: str) -> bool:
    """Validate WireGuard public/private key format (base64, 44 chars)"""
    if not key or len(key) != 44:
        return False
    pattern = r'^[A-Za-z0-9+/]{43}=$'
    return bool(re.match(pattern, key))

# SQL Injection prevention
DANGEROUS_SQL_PATTERNS = [
    r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
    r'(--|;|\/\*|\*\/)',
    r'(\bOR\b.*=.*)',
    r'(\bAND\b.*=.*)',
    r'(\'.*\')',
    r'(\bUNION\b)',
]

def contains_sql_injection(value: str) -> bool:
    """Check if string contains potential SQL injection patterns"""
    if not value:
        return False
    value_upper = value.upper()
    for pattern in DANGEROUS_SQL_PATTERNS:
        if re.search(pattern, value_upper, re.IGNORECASE):
            return True
    return False

# XSS prevention
XSS_PATTERNS = [
    r'<script[^>]*>.*?</script>',
    r'javascript:',
    r'on\w+\s*=',
    r'<iframe',
    r'<object',
    r'<embed',
]

def contains_xss(value: str) -> bool:
    """Check if string contains potential XSS patterns"""
    if not value:
        return False
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value, re.IGNORECASE):
            return True
    return False

def validate_safe_string(value: str, max_length: int = 255) -> tuple[bool, str]:
    """
    Comprehensive string validation
    Returns (is_valid, error_message)
    """
    if not value:
        return False, "Value cannot be empty"
    
    if len(value) > max_length:
        return False, f"Value exceeds maximum length of {max_length}"
    
    if contains_sql_injection(value):
        return False, "Value contains potentially dangerous SQL patterns"
    
    if contains_xss(value):
        return False, "Value contains potentially dangerous XSS patterns"
    
    return True, ""
