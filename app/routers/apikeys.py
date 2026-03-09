"""API Keys management endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional
import secrets
import hashlib
from app.services import db
from app.routers.users import get_current_user

router = APIRouter()

class CreateAPIKeyRequest(BaseModel):
    name: str
    expires_days: Optional[int] = None  # None = never expires

@router.post("/", status_code=201)
async def create_api_key(
    body: CreateAPIKeyRequest,
    user: dict = Depends(get_current_user)
):
    """Create new API key"""
    user_id = user["sub"]
    
    # Generate API key
    api_key = f"vpn_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Calculate expiration
    expires_at = None
    if body.expires_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_days)
    
    pool = await db.get_pool()
    result = await pool.fetchrow(
        """INSERT INTO api_keys (user_id, key_hash, name, expires_at)
           VALUES ($1, $2, $3, $4)
           RETURNING id, name, created_at, expires_at""",
        user_id, key_hash, body.name, expires_at
    )
    
    return {
        "api_key": api_key,  # Only shown once!
        "id": str(result["id"]),
        "name": result["name"],
        "created_at": result["created_at"].isoformat(),
        "expires_at": result["expires_at"].isoformat() if result["expires_at"] else None,
        "warning": "Save this key now. You won't be able to see it again!"
    }

@router.get("/", status_code=200)
async def list_api_keys(user: dict = Depends(get_current_user)):
    """List all API keys for user"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    keys = await pool.fetch(
        """SELECT id, name, last_used, is_active, created_at, expires_at
           FROM api_keys 
           WHERE user_id = $1 
           ORDER BY created_at DESC""",
        user_id
    )
    
    return {"api_keys": [dict(k) for k in keys]}

@router.delete("/{key_id}", status_code=204)
async def revoke_api_key(
    key_id: str,
    user: dict = Depends(get_current_user)
):
    """Revoke API key"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    result = await pool.execute(
        "UPDATE api_keys SET is_active = FALSE WHERE id = $1 AND user_id = $2",
        key_id, user_id
    )
    
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="API key not found")

async def verify_api_key(api_key: str) -> Optional[dict]:
    """Verify API key and return user info"""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    pool = await db.get_pool()
    result = await pool.fetchrow(
        """SELECT ak.user_id, ak.id as key_id, u.role, u.is_active, u.is_banned
           FROM api_keys ak
           JOIN users u ON ak.user_id = u.id
           WHERE ak.key_hash = $1 
           AND ak.is_active = TRUE
           AND (ak.expires_at IS NULL OR ak.expires_at > NOW())""",
        key_hash
    )
    
    if result:
        # Update last_used
        await pool.execute(
            "UPDATE api_keys SET last_used = NOW() WHERE id = $1",
            result["key_id"]
        )
        
        return dict(result)
    
    return None
