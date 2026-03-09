from pydantic import BaseModel
from typing import Optional

class VpnConfigRequest(BaseModel):
    device_id: str
    client_public_key: str          # WireGuard public key generated on device
    server_id: Optional[str] = None # UUID of chosen server from /vpn/servers

class VpnConfigResponse(BaseModel):
    interface_address: str          # e.g., "10.8.0.5/32"
    dns: str
    server_public_key: str
    server_endpoint: str
    allowed_ips: str
    preshared_key: str              # Adds symmetric PQ layer to WireGuard
    signature: str                  # Ed25519 signature of entire config JSON
    config_id: str
    country: Optional[str] = None
    country_code: Optional[str] = None

class VpnServerResponse(BaseModel):
    id: str
    country: str
    country_code: str
    city: str | None
    load_percent: int
    is_premium: bool

class VpnConfigRequestWithServer(BaseModel):
    server_id: str
    device_id: str
    client_public_key: str
