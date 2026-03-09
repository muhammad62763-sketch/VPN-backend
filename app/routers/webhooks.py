"""Webhook endpoints for external integrations"""
from fastapi import APIRouter, HTTPException, Header, Request
from pydantic import BaseModel
from typing import Optional
import hmac
import hashlib
from app.services import db, security_service
from app.config import settings

router = APIRouter()

class WebhookPayload(BaseModel):
    event: str
    data: dict
    timestamp: str

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature using HMAC-SHA256"""
    expected = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@router.post("/vpn-connection")
async def vpn_connection_webhook(
    request: Request,
    x_webhook_signature: str = Header(...)
):
    """Handle VPN connection status updates from WireGuard server"""
    body = await request.body()
    
    if not verify_webhook_signature(body, x_webhook_signature, settings.JWT_SECRET_KEY):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    event_type = payload.get("event")  # "connected" or "disconnected"
    config_id = payload.get("config_id")
    bytes_sent = payload.get("bytes_sent", 0)
    bytes_received = payload.get("bytes_received", 0)
    
    if event_type == "disconnected" and config_id:
        pool = await db.get_pool()
        
        # Update connection record
        await pool.execute(
            """UPDATE vpn_connections 
               SET disconnected_at = NOW(),
                   bytes_sent = $1,
                   bytes_received = $2,
                   duration_seconds = EXTRACT(EPOCH FROM (NOW() - connected_at))::INT
               WHERE config_id = $3 AND disconnected_at IS NULL""",
            bytes_sent, bytes_received, config_id
        )
    
    return {"status": "processed"}

@router.post("/security-alert")
async def security_alert_webhook(
    request: Request,
    x_webhook_signature: str = Header(...)
):
    """Handle security alerts from external monitoring"""
    body = await request.body()
    
    if not verify_webhook_signature(body, x_webhook_signature, settings.JWT_SECRET_KEY):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    alert_type = payload.get("alert_type")
    user_id = payload.get("user_id")
    details = payload.get("details", {})
    
    if user_id:
        await security_service.log_security_event(
            user_id, f"external_alert_{alert_type}",
            payload.get("ip_address", "unknown"),
            metadata=details,
            severity="critical"
        )
    
    return {"status": "processed"}
