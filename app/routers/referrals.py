"""Referral system endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import secrets
import string
from app.services import db
from app.routers.users import get_current_user

router = APIRouter()

class CreateReferralCodeRequest(BaseModel):
    max_uses: Optional[int] = None  # None = unlimited
    reward_days: int = 7

def generate_referral_code() -> str:
    """Generate unique referral code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(8))

@router.post("/create", status_code=201)
async def create_referral_code(
    body: CreateReferralCodeRequest,
    user: dict = Depends(get_current_user)
):
    """Create referral code"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Generate unique code
    while True:
        code = generate_referral_code()
        existing = await pool.fetchval(
            "SELECT id FROM referral_codes WHERE code = $1",
            code
        )
        if not existing:
            break
    
    result = await pool.fetchrow(
        """INSERT INTO referral_codes (user_id, code, max_uses, reward_days)
           VALUES ($1, $2, $3, $4)
           RETURNING *""",
        user_id, code, body.max_uses, body.reward_days
    )
    
    return dict(result)

@router.get("/my-codes", status_code=200)
async def get_my_referral_codes(user: dict = Depends(get_current_user)):
    """Get user's referral codes"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    codes = await pool.fetch(
        """SELECT * FROM referral_codes 
           WHERE user_id = $1 
           ORDER BY created_at DESC""",
        user_id
    )
    
    return {"referral_codes": [dict(c) for c in codes]}

@router.get("/stats", status_code=200)
async def get_referral_stats(user: dict = Depends(get_current_user)):
    """Get referral statistics"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Total referrals
    total_referrals = await pool.fetchval(
        "SELECT COUNT(*) FROM referral_usage WHERE referrer_user_id = $1",
        user_id
    )
    
    # Total uses across all codes
    total_uses = await pool.fetchval(
        "SELECT SUM(uses_count) FROM referral_codes WHERE user_id = $1",
        user_id
    )
    
    # Active codes
    active_codes = await pool.fetchval(
        "SELECT COUNT(*) FROM referral_codes WHERE user_id = $1 AND is_active = TRUE",
        user_id
    )
    
    return {
        "total_referrals": total_referrals or 0,
        "total_uses": total_uses or 0,
        "active_codes": active_codes or 0
    }

@router.post("/apply/{code}", status_code=200)
async def apply_referral_code(
    code: str,
    user: dict = Depends(get_current_user)
):
    """Apply referral code (for new users)"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Get referral code
    referral = await pool.fetchrow(
        """SELECT * FROM referral_codes 
           WHERE code = $1 AND is_active = TRUE""",
        code
    )
    
    if not referral:
        raise HTTPException(status_code=404, detail="Invalid referral code")
    
    # Check if user already used a referral
    existing = await pool.fetchval(
        "SELECT id FROM referral_usage WHERE referred_user_id = $1",
        user_id
    )
    
    if existing:
        raise HTTPException(status_code=400, detail="You have already used a referral code")
    
    # Check if user is trying to use their own code
    if str(referral["user_id"]) == user_id:
        raise HTTPException(status_code=400, detail="Cannot use your own referral code")
    
    # Check max uses
    if referral["max_uses"] and referral["uses_count"] >= referral["max_uses"]:
        raise HTTPException(status_code=400, detail="Referral code has reached maximum uses")
    
    # Apply referral
    await pool.execute(
        """INSERT INTO referral_usage (referral_code_id, referred_user_id, referrer_user_id)
           VALUES ($1, $2, $3)""",
        referral["id"], user_id, referral["user_id"]
    )
    
    # Increment uses count
    await pool.execute(
        "UPDATE referral_codes SET uses_count = uses_count + 1 WHERE id = $1",
        referral["id"]
    )
    
    # Grant premium to referrer (reward_days)
    from datetime import datetime, timezone, timedelta
    premium_until = datetime.now(timezone.utc) + timedelta(days=referral["reward_days"])
    
    await pool.execute(
        """UPDATE users 
           SET is_premium = TRUE,
               premium_expires_at = CASE 
                   WHEN premium_expires_at IS NULL OR premium_expires_at < NOW() 
                   THEN $1
                   ELSE premium_expires_at + INTERVAL '1 day' * $2
               END
           WHERE id = $3""",
        premium_until, referral["reward_days"], referral["user_id"]
    )
    
    return {
        "message": "Referral code applied successfully",
        "referrer_rewarded_days": referral["reward_days"]
    }

@router.delete("/{code_id}", status_code=204)
async def deactivate_referral_code(
    code_id: str,
    user: dict = Depends(get_current_user)
):
    """Deactivate referral code"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    result = await pool.execute(
        "UPDATE referral_codes SET is_active = FALSE WHERE id = $1 AND user_id = $2",
        code_id, user_id
    )
    
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Referral code not found")
