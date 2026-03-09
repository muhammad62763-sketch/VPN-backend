"""Bandwidth tracking and management endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from app.services import db
from app.routers.users import get_current_user

router = APIRouter()

@router.get("/usage", status_code=200)
async def get_bandwidth_usage(
    days: int = 30,
    user: dict = Depends(get_current_user)
):
    """Get bandwidth usage for period"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    usage = await pool.fetch(
        """SELECT * FROM bandwidth_usage 
           WHERE user_id = $1 AND period_start >= $2
           ORDER BY period_start DESC""",
        user_id, start_date
    )
    
    # Calculate total
    total_bytes = sum(row["bytes_used"] for row in usage)
    
    # Get user limit
    db_user = await db.get_user_by_id(user_id)
    limit = db_user.get("bandwidth_limit")
    
    return {
        "usage_records": [dict(u) for u in usage],
        "total_bytes_used": total_bytes,
        "bandwidth_limit": limit,
        "percentage_used": (total_bytes / limit * 100) if limit else 0,
        "period_days": days
    }

@router.get("/current-period", status_code=200)
async def get_current_period_usage(user: dict = Depends(get_current_user)):
    """Get current billing period usage"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Current month
    now = datetime.now(timezone.utc)
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    usage = await pool.fetchrow(
        """SELECT SUM(bytes_used) as total_bytes
           FROM bandwidth_usage 
           WHERE user_id = $1 AND period_start >= $2""",
        user_id, period_start
    )
    
    # Get user limit
    db_user = await db.get_user_by_id(user_id)
    limit = db_user.get("bandwidth_limit")
    
    total_bytes = usage["total_bytes"] or 0
    
    return {
        "period_start": period_start.isoformat(),
        "period_end": (period_start + timedelta(days=32)).replace(day=1).isoformat(),
        "bytes_used": total_bytes,
        "bandwidth_limit": limit,
        "percentage_used": (total_bytes / limit * 100) if limit else 0,
        "remaining_bytes": (limit - total_bytes) if limit else None
    }

async def track_bandwidth(user_id: str, bytes_used: int):
    """Helper function to track bandwidth usage"""
    pool = await db.get_pool()
    
    # Current hour period
    now = datetime.now(timezone.utc)
    period_start = now.replace(minute=0, second=0, microsecond=0)
    period_end = period_start + timedelta(hours=1)
    
    # Update or insert
    await pool.execute(
        """INSERT INTO bandwidth_usage (user_id, bytes_used, period_start, period_end)
           VALUES ($1, $2, $3, $4)
           ON CONFLICT (user_id, period_start) 
           DO UPDATE SET bytes_used = bandwidth_usage.bytes_used + $2""",
        user_id, bytes_used, period_start, period_end
    )
    
    # Check if user exceeded limit
    db_user = await db.get_user_by_id(user_id)
    if db_user.get("bandwidth_limit"):
        # Get current month usage
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total = await pool.fetchval(
            """SELECT SUM(bytes_used) FROM bandwidth_usage 
               WHERE user_id = $1 AND period_start >= $2""",
            user_id, month_start
        )
        
        if total and total >= db_user["bandwidth_limit"]:
            # Send notification
            from app.routers.notifications import create_notification
            await create_notification(
                user_id,
                "Bandwidth Limit Reached",
                f"You have used {total / 1024 / 1024 / 1024:.2f} GB of your {db_user['bandwidth_limit'] / 1024 / 1024 / 1024:.2f} GB limit",
                "warning"
            )
