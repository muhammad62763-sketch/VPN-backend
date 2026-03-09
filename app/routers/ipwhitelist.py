"""IP Whitelist management endpoints (Admin only)"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from app.services import db, auth_service
from app.routers.admin import require_admin

router = APIRouter()

class AddIPRequest(BaseModel):
    ip_address: str
    description: Optional[str] = None

@router.get("/", status_code=200)
async def list_whitelisted_ips(admin: dict = Depends(require_admin)):
    """List all whitelisted IPs"""
    pool = await db.get_pool()
    
    ips = await pool.fetch(
        """SELECT iw.*, u.email as created_by_email
           FROM ip_whitelist iw
           LEFT JOIN users u ON iw.created_by = u.id
           ORDER BY iw.created_at DESC"""
    )
    
    return {"whitelisted_ips": [dict(ip) for ip in ips]}

@router.post("/", status_code=201)
async def add_ip_to_whitelist(
    body: AddIPRequest,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Add IP to whitelist"""
    from app.utils.ip_utils import is_valid_ip
    
    if not is_valid_ip(body.ip_address):
        raise HTTPException(status_code=400, detail="Invalid IP address")
    
    pool = await db.get_pool()
    
    # Check if already exists
    existing = await pool.fetchval(
        "SELECT id FROM ip_whitelist WHERE ip_address = $1",
        body.ip_address
    )
    
    if existing:
        raise HTTPException(status_code=409, detail="IP already whitelisted")
    
    result = await pool.fetchrow(
        """INSERT INTO ip_whitelist (ip_address, description, created_by)
           VALUES ($1, $2, $3)
           RETURNING *""",
        body.ip_address, body.description, admin["sub"]
    )
    
    # Log audit
    await db.log_audit(
        actor_id=admin["sub"],
        action="add_ip_whitelist",
        target_id=body.ip_address,
        metadata={"description": body.description},
        ip_address=request.client.host
    )
    
    return dict(result)

@router.delete("/{ip_id}", status_code=204)
async def remove_ip_from_whitelist(
    ip_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Remove IP from whitelist"""
    pool = await db.get_pool()
    
    # Get IP before deleting for audit
    ip_record = await pool.fetchrow(
        "SELECT ip_address FROM ip_whitelist WHERE id = $1",
        ip_id
    )
    
    if not ip_record:
        raise HTTPException(status_code=404, detail="IP not found")
    
    await pool.execute("DELETE FROM ip_whitelist WHERE id = $1", ip_id)
    
    # Log audit
    await db.log_audit(
        actor_id=admin["sub"],
        action="remove_ip_whitelist",
        target_id=ip_record["ip_address"],
        ip_address=request.client.host
    )

@router.patch("/{ip_id}/toggle", status_code=200)
async def toggle_ip_status(
    ip_id: str,
    request: Request,
    admin: dict = Depends(require_admin)
):
    """Toggle IP whitelist status"""
    pool = await db.get_pool()
    
    result = await pool.fetchrow(
        """UPDATE ip_whitelist 
           SET is_active = NOT is_active 
           WHERE id = $1
           RETURNING *""",
        ip_id
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="IP not found")
    
    # Log audit
    await db.log_audit(
        actor_id=admin["sub"],
        action="toggle_ip_whitelist",
        target_id=result["ip_address"],
        metadata={"is_active": result["is_active"]},
        ip_address=request.client.host
    )
    
    return dict(result)

async def is_ip_whitelisted(ip_address: str) -> bool:
    """Check if IP is whitelisted"""
    pool = await db.get_pool()
    
    result = await pool.fetchval(
        "SELECT id FROM ip_whitelist WHERE ip_address = $1 AND is_active = TRUE",
        ip_address
    )
    
    return result is not None
