"""Notifications endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services import db
from app.routers.users import get_current_user

router = APIRouter()

class CreateNotificationRequest(BaseModel):
    title: str
    message: str
    type: str = "info"  # info, warning, error, success

@router.get("/", status_code=200)
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    if unread_only:
        notifications = await pool.fetch(
            """SELECT * FROM notifications 
               WHERE user_id = $1 AND is_read = FALSE 
               ORDER BY created_at DESC LIMIT $2""",
            user_id, limit
        )
    else:
        notifications = await pool.fetch(
            """SELECT * FROM notifications 
               WHERE user_id = $1 
               ORDER BY created_at DESC LIMIT $2""",
            user_id, limit
        )
    
    return {"notifications": [dict(n) for n in notifications]}

@router.get("/unread-count", status_code=200)
async def get_unread_count(user: dict = Depends(get_current_user)):
    """Get unread notification count"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    count = await pool.fetchval(
        "SELECT COUNT(*) FROM notifications WHERE user_id = $1 AND is_read = FALSE",
        user_id
    )
    
    return {"unread_count": count}

@router.post("/{notification_id}/read", status_code=200)
async def mark_as_read(
    notification_id: str,
    user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Verify notification belongs to user
    notification = await pool.fetchrow(
        "SELECT * FROM notifications WHERE id = $1 AND user_id = $2",
        notification_id, user_id
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    await pool.execute(
        "UPDATE notifications SET is_read = TRUE WHERE id = $1",
        notification_id
    )
    
    return {"message": "Notification marked as read"}

@router.post("/read-all", status_code=200)
async def mark_all_as_read(user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    await pool.execute(
        "UPDATE notifications SET is_read = TRUE WHERE user_id = $1 AND is_read = FALSE",
        user_id
    )
    
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete notification"""
    user_id = user["sub"]
    pool = await db.get_pool()
    
    # Verify notification belongs to user
    result = await pool.execute(
        "DELETE FROM notifications WHERE id = $1 AND user_id = $2",
        notification_id, user_id
    )
    
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Notification not found")

async def create_notification(user_id: str, title: str, message: str, type: str = "info"):
    """Helper function to create notification"""
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO notifications (user_id, title, message, type)
           VALUES ($1, $2, $3, $4)""",
        user_id, title, message, type
    )
