"""Background task scheduler for maintenance tasks"""
import asyncio
from datetime import datetime, timezone
from app.services import security_service, db

async def cleanup_expired_sessions():
    """Cleanup expired sessions and old data"""
    try:
        await security_service.cleanup_expired_data()
        print(f"[{datetime.now(timezone.utc)}] Cleaned up expired data")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Error cleaning up data: {e}")

async def update_server_load():
    """Update VPN server load percentages"""
    try:
        pool = await db.get_pool()
        servers = await pool.fetch("SELECT id FROM vpn_servers WHERE is_active = TRUE")
        
        for server in servers:
            # In production, query actual server metrics
            # For now, simulate with random load
            import random
            load = random.randint(10, 90)
            await pool.execute(
                "UPDATE vpn_servers SET load_percent = $1 WHERE id = $2",
                load, server["id"]
            )
        
        print(f"[{datetime.now(timezone.utc)}] Updated server load metrics")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Error updating server load: {e}")

async def disconnect_idle_vpn_connections():
    """Mark VPN connections as disconnected if idle for too long"""
    try:
        pool = await db.get_pool()
        # Disconnect connections idle for more than 24 hours
        result = await pool.execute(
            """UPDATE vpn_connections 
               SET disconnected_at = NOW(),
                   duration_seconds = EXTRACT(EPOCH FROM (NOW() - connected_at))::INT
               WHERE disconnected_at IS NULL 
               AND connected_at < NOW() - INTERVAL '24 hours'"""
        )
        print(f"[{datetime.now(timezone.utc)}] Disconnected idle VPN connections")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Error disconnecting idle connections: {e}")

async def run_scheduler():
    """Main scheduler loop"""
    print(f"[{datetime.now(timezone.utc)}] Background scheduler started")
    
    while True:
        try:
            # Run cleanup every 1 hour
            await cleanup_expired_sessions()
            
            # Update server load every 5 minutes
            await update_server_load()
            
            # Disconnect idle connections every 30 minutes
            await disconnect_idle_vpn_connections()
            
            # Wait 5 minutes before next cycle
            await asyncio.sleep(300)
            
        except Exception as e:
            print(f"[{datetime.now(timezone.utc)}] Scheduler error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error
