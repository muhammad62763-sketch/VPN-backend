import base64
import os
import ipaddress
import hmac
import hashlib
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)

def generate_wireguard_keypair() -> tuple[str, str]:
    """
    Generate a WireGuard keypair (X25519).
    Returns (private_key_b64, public_key_b64).
    """
    private_key = X25519PrivateKey.generate()
    priv_bytes = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    pub_bytes = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.b64encode(priv_bytes).decode(), base64.b64encode(pub_bytes).decode()

def generate_preshared_key() -> str:
    """
    Generate a 32-byte cryptographically random PSK.
    This adds a symmetric layer to WireGuard for post-quantum resistance.
    Ideally derived from QRNG entropy; falls back to OS CSPRNG.
    """
    return base64.b64encode(os.urandom(32)).decode()

def allocate_client_ip(user_id: str) -> str:
    """
    Deterministically allocate a /32 from 10.8.0.0/16 based on user_id hash.
    In production, use a DB-backed IPAM table to prevent collisions.
    """
    hash_bytes = hashlib.sha256(user_id.encode()).digest()
    octet3 = hash_bytes[0] % 256
    octet4 = (hash_bytes[1] % 254) + 1   # avoid .0 and .255
    return f"10.8.{octet3}.{octet4}/32"

def build_wg_config_block(
    client_private_key: str,
    client_address: str,
    dns: str,
    server_public_key: str,
    preshared_key: str,
    endpoint: str,
    allowed_ips: str,
) -> str:
    """Build a WireGuard .conf file string."""
    return f"""[Interface]
PrivateKey = {client_private_key}
Address = {client_address}
DNS = {dns}

[Peer]
PublicKey = {server_public_key}
PresharedKey = {preshared_key}
Endpoint = {endpoint}
AllowedIPs = {allowed_ips}
PersistentKeepalive = 25
"""
