"""Email service for sending notifications"""
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional
from app.services import db

# In production, integrate with SendGrid, AWS SES, or similar
# For now, this is a placeholder that logs emails

async def send_email(to: str, subject: str, body: str, html: Optional[str] = None):
    """Send email (placeholder - integrate with actual email service)"""
    print(f"""
    ═══════════════════════════════════════════════════════════
    📧 EMAIL SENT
    ═══════════════════════════════════════════════════════════
    To: {to}
    Subject: {subject}
    
    {body}
    ═══════════════════════════════════════════════════════════
    """)
    # TODO: Integrate with actual email service
    # Example: SendGrid, AWS SES, Mailgun, etc.
    pass

async def generate_verification_token(user_id: str) -> str:
    """Generate email verification token"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO email_verification_tokens (user_id, token_hash, expires_at)
           VALUES ($1, $2, $3)""",
        user_id, token_hash, expires_at
    )
    
    return token

async def verify_email_token(token: str) -> Optional[str]:
    """Verify email token and return user_id if valid"""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    pool = await db.get_pool()
    result = await pool.fetchrow(
        """SELECT user_id FROM email_verification_tokens
           WHERE token_hash = $1 
           AND expires_at > NOW()
           AND is_used = FALSE""",
        token_hash
    )
    
    if result:
        # Mark token as used
        await pool.execute(
            "UPDATE email_verification_tokens SET is_used = TRUE WHERE token_hash = $1",
            token_hash
        )
        
        # Mark user email as verified
        await pool.execute(
            "UPDATE users SET email_verified = TRUE WHERE id = $1",
            result["user_id"]
        )
        
        return str(result["user_id"])
    
    return None

async def send_verification_email(user_id: str, email: str, base_url: str):
    """Send email verification link"""
    token = await generate_verification_token(user_id)
    verification_link = f"{base_url}/verify-email?token={token}"
    
    subject = "Verify your email address"
    body = f"""
    Welcome to VPN Backend!
    
    Please verify your email address by clicking the link below:
    {verification_link}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    """
    
    await send_email(email, subject, body)

async def generate_password_reset_token(user_id: str) -> str:
    """Generate password reset token"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    pool = await db.get_pool()
    await pool.execute(
        """INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
           VALUES ($1, $2, $3)""",
        user_id, token_hash, expires_at
    )
    
    return token

async def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return user_id if valid"""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    pool = await db.get_pool()
    result = await pool.fetchrow(
        """SELECT user_id FROM password_reset_tokens
           WHERE token_hash = $1 
           AND expires_at > NOW()
           AND is_used = FALSE""",
        token_hash
    )
    
    if result:
        # Mark token as used
        await pool.execute(
            "UPDATE password_reset_tokens SET is_used = TRUE WHERE token_hash = $1",
            token_hash
        )
        return str(result["user_id"])
    
    return None

async def send_password_reset_email(user_id: str, email: str, base_url: str):
    """Send password reset link"""
    token = await generate_password_reset_token(user_id)
    reset_link = f"{base_url}/reset-password?token={token}"
    
    subject = "Reset your password"
    body = f"""
    You requested to reset your password.
    
    Click the link below to reset your password:
    {reset_link}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email and your password will remain unchanged.
    """
    
    await send_email(email, subject, body)

async def send_security_alert(user_id: str, email: str, alert_type: str, details: dict):
    """Send security alert email"""
    subject = f"Security Alert: {alert_type}"
    body = f"""
    We detected a security event on your account:
    
    Type: {alert_type}
    Time: {datetime.now(timezone.utc).isoformat()}
    Details: {details}
    
    If this was you, no action is needed.
    If this wasn't you, please secure your account immediately.
    """
    
    await send_email(email, subject, body)
