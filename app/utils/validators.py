import re
import base64
from uuid import UUID

def validate_uuid(value: str) -> bool:
    """Returns True if value is a valid UUID v4 string."""
    try:
        UUID(value, version=4)
        return True
    except (ValueError, AttributeError):
        return False

def validate_base64_key(value: str, expected_bytes: int = 32) -> bool:
    """
    Validate a base64-encoded key of expected byte length.
    Used to validate WireGuard public keys (32 bytes).
    """
    try:
        decoded = base64.b64decode(value, validate=True)
        return len(decoded) == expected_bytes
    except Exception:
        return False

def validate_ip_cidr(value: str) -> bool:
    """Check if a string is a valid IPv4 CIDR notation like 10.8.0.5/32."""
    pattern = r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$"
    return bool(re.match(pattern, value))

def sanitize_string(value: str, max_length: int = 255) -> str:
    """Strip whitespace and truncate to max_length."""
    return value.strip()[:max_length]
