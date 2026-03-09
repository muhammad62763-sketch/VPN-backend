#!/usr/bin/env python3
"""Generate Ed25519 key pair for config signing."""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)

private_key = Ed25519PrivateKey.generate()

priv_bytes = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
pub_bytes = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

print("ED25519_PRIVATE_KEY_HEX =", priv_bytes.hex())
print("ED25519_PUBLIC_KEY_HEX  =", pub_bytes.hex())
print("\nAdd the private key to your .env file")
print("Save the public key for client-side verification")
