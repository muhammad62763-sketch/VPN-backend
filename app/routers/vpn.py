from fastapi import APIRouter, Depends, HTTPException, Header, Request
from app.models.vpn import VpnConfigRequest, VpnConfigResponse, VpnServerResponse, VpnConfigRequestWithServer
from app.services import wireguard_service, crypto_service, auth_service, db, security_service
from app.config import settings

router = APIRouter()

async def get_current_user(authorization: str = Header(...), x_device_id: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.removeprefix("Bearer ")
    payload = auth_service.decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token")
    if not auth_service.verify_device_binding(payload, x_device_id):
        raise HTTPException(status_code=401, detail="Device mismatch")
    
    # Check if session is still valid
    jti = payload.get("jti")
    if jti and not await security_service.is_session_valid(jti):
        raise HTTPException(status_code=401, detail="Session expired or revoked")
    
    return payload

@router.get("/servers")
async def list_servers(user: dict = Depends(get_current_user)):
    """Return all available VPN servers for the country picker UI."""
    pool = await db.get_pool()
    rows = await pool.fetch(
        "SELECT id, country, country_code, city, load_percent, is_premium "
        "FROM vpn_servers WHERE is_active = TRUE ORDER BY country ASC"
    )
    return {"servers": [dict(r) for r in rows]}

@router.post("/config", response_model=VpnConfigResponse)
async def get_vpn_config(
    body: VpnConfigRequestWithServer,
    request: Request,
    user: dict = Depends(get_current_user),
):
    user_id = user["sub"]
    
    # Check if user has reached max devices
    pool = await db.get_pool()
    device_count = await pool.fetchval(
        "SELECT COUNT(*) FROM vpn_configs WHERE user_id = $1 AND is_revoked = FALSE",
        user_id
    )
    
    # Superadmins have no device limit
    if not auth_service.is_superadmin(user) and device_count >= settings.MAX_DEVICES_PER_USER:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum {settings.MAX_DEVICES_PER_USER} devices reached. Revoke a config first."
        )
    
    # Fetch specific server by server_id from DB
    server = await pool.fetchrow(
        "SELECT * FROM vpn_servers WHERE id = $1 AND is_active = TRUE",
        body.server_id
    )
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    # Check if server is premium and user has access
    if server["is_premium"]:
        db_user = await db.get_user_by_id(user_id)
        if not db_user.get("is_premium") and not auth_service.is_admin(user):
            raise HTTPException(status_code=403, detail="Premium server requires premium subscription")
    
    psk = wireguard_service.generate_preshared_key()
    client_ip = wireguard_service.allocate_client_ip(user_id)
    config_id = crypto_service.generate_config_id()

    config_data = {
        "interface_address": client_ip,
        "dns": settings.WG_DNS,
        "server_public_key": server["public_key"],
        "server_endpoint": server["endpoint"],
        "allowed_ips": "0.0.0.0/0, ::/0",
        "preshared_key": psk,
        "config_id": config_id,
    }

    # Sign the entire config to prove authenticity
    signature = crypto_service.sign_payload(config_data)
    
    # Store config in database
    await pool.execute(
        """INSERT INTO vpn_configs (user_id, config_id, client_ip, server_id, preshared_key)
           VALUES ($1, $2, $3, $4, $5)""",
        user_id, config_id, client_ip, body.server_id, psk
    )
    
    # Log VPN connection
    await security_service.log_vpn_connection(
        user_id, config_id, str(body.server_id), request.client.host
    )
    
    # Log security event
    await security_service.log_security_event(
        user_id, "vpn_config_created", request.client.host,
        request.headers.get("user-agent"), user.get("device"),
        {"config_id": config_id, "server_id": str(body.server_id)}
    )

    return VpnConfigResponse(**config_data, signature=signature)

@router.delete("/config/{config_id}", status_code=204)
async def revoke_vpn_config(
    config_id: str,
    request: Request,
    user: dict = Depends(get_current_user),
):
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Verify config belongs to user
    config = await pool.fetchrow(
        "SELECT * FROM vpn_configs WHERE config_id = $1",
        config_id
    )
    
    if not config:
        raise HTTPException(status_code=404, detail="Config not found")
    
    if str(config["user_id"]) != user_id and not auth_service.is_admin(user):
        raise HTTPException(status_code=403, detail="Not authorized to revoke this config")
    
    # Mark as revoked
    await pool.execute(
        "UPDATE vpn_configs SET is_revoked = TRUE WHERE config_id = $1",
        config_id
    )
    
    # Release IP back to pool
    await pool.execute(
        "UPDATE ip_pool SET is_assigned = FALSE WHERE ip_address = $1",
        config["client_ip"]
    )
    
    # Log security event
    await security_service.log_security_event(
        user_id, "vpn_config_revoked", request.client.host,
        request.headers.get("user-agent"), user.get("device"),
        {"config_id": config_id}
    )

@router.get("/stats")
async def get_vpn_stats(user: dict = Depends(get_current_user)):
    """Get user's VPN usage statistics"""
    user_id = user["sub"]
    stats = await security_service.get_connection_stats(user_id)
    
    pool = await db.get_pool()
    active_configs = await pool.fetchval(
        "SELECT COUNT(*) FROM vpn_configs WHERE user_id = $1 AND is_revoked = FALSE",
        user_id
    )
    
    return {
        "active_configs": active_configs,
        "max_devices": None if auth_service.is_superadmin(user) else settings.MAX_DEVICES_PER_USER,
        "total_connections": stats.get("total_connections", 0),
        "total_bytes_sent": stats.get("total_sent", 0),
        "total_bytes_received": stats.get("total_received", 0),
        "avg_duration_seconds": stats.get("avg_duration", 0),
    }
