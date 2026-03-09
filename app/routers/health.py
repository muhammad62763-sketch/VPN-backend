from fastapi import APIRouter
from datetime import datetime, timezone
from app.services import db

router = APIRouter()

@router.get("/health")
async def health():
    """Basic health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
    }

@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with database connectivity"""
    db_status = "ok"
    db_latency = None
    
    try:
        pool = await db.get_pool()
        start = datetime.now(timezone.utc)
        await pool.fetchval("SELECT 1")
        end = datetime.now(timezone.utc)
        db_latency = (end - start).total_seconds() * 1000  # ms
    except Exception as e:
        db_status = "error"
        db_latency = None
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "2.0.0",
        "components": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency
            }
        }
    }
