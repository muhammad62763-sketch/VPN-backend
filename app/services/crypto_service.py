import json
import os
import hmac
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from app.config import settings

def _load_signing_key() -> Ed25519PrivateKey:
    """Load Ed25519 signing key from environment (hex-encoded)."""
    key_bytes = bytes.fromhex(settings.ED25519_PRIVATE_KEY_HEX)
    return Ed25519PrivateKey.from_private_bytes(key_bytes)

def sign_payload(payload: dict) -> str:
    """
    Sign a JSON payload with Ed25519.
    Returns base64-encoded signature string.
    Used to prove VPN config came from this server (authenticity).
    """
    key = _load_signing_key()
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    signature = key.sign(payload_bytes)
    return base64.b64encode(signature).decode()

def verify_hmac(data: bytes, received_mac: str, secret: str) -> bool:
    """Verify HMAC-SHA256 for integrity checking of API payloads."""
    expected = hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_mac)

def generate_config_id() -> str:
    """Generate a unique config ID using OS CSPRNG."""
    return base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip("=")
