"""TOTP/2FA service for two-factor authentication"""
import pyotp
import qrcode
import io
import base64
from typing import Tuple, List
from app.services import db

def generate_totp_secret() -> str:
    """Generate a new TOTP secret"""
    return pyotp.random_base32()

def generate_qr_code(email: str, secret: str, issuer: str = "VPN Backend") -> str:
    """Generate QR code for TOTP setup"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name=issuer)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def verify_totp_code(secret: str, code: str) -> bool:
    """Verify TOTP code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 1 step before/after

def generate_backup_codes(count: int = 10) -> List[str]:
    """Generate backup codes for 2FA recovery"""
    import secrets
    return [f"{secrets.randbelow(10000):04d}-{secrets.randbelow(10000):04d}" for _ in range(count)]

async def enable_2fa(user_id: str) -> Tuple[str, str, List[str]]:
    """Enable 2FA for user and return secret, QR code, and backup codes"""
    secret = generate_totp_secret()
    backup_codes = generate_backup_codes()
    
    # Hash backup codes before storing
    import hashlib
    hashed_codes = [hashlib.sha256(code.encode()).hexdigest() for code in backup_codes]
    
    pool = await db.get_pool()
    
    # Get user email for QR code
    user = await pool.fetchrow("SELECT email FROM users WHERE id = $1", user_id)
    if not user:
        raise ValueError("User not found")
    
    # Store secret and backup codes
    await pool.execute(
        """UPDATE users 
           SET totp_secret = $1, 
               backup_codes = $2,
               totp_enabled = FALSE
           WHERE id = $3""",
        secret, hashed_codes, user_id
    )
    
    qr_code = generate_qr_code(user["email"], secret)
    
    return secret, qr_code, backup_codes

async def confirm_2fa_setup(user_id: str, code: str) -> bool:
    """Confirm 2FA setup by verifying first code"""
    pool = await db.get_pool()
    user = await pool.fetchrow(
        "SELECT totp_secret FROM users WHERE id = $1",
        user_id
    )
    
    if not user or not user["totp_secret"]:
        return False
    
    if verify_totp_code(user["totp_secret"], code):
        # Enable 2FA
        await pool.execute(
            "UPDATE users SET totp_enabled = TRUE WHERE id = $1",
            user_id
        )
        return True
    
    return False

async def disable_2fa(user_id: str):
    """Disable 2FA for user"""
    pool = await db.get_pool()
    await pool.execute(
        """UPDATE users 
           SET totp_enabled = FALSE,
               totp_secret = NULL,
               backup_codes = NULL
           WHERE id = $1""",
        user_id
    )

async def verify_2fa_code(user_id: str, code: str) -> bool:
    """Verify 2FA code (TOTP or backup code)"""
    pool = await db.get_pool()
    user = await pool.fetchrow(
        "SELECT totp_secret, backup_codes FROM users WHERE id = $1",
        user_id
    )
    
    if not user:
        return False
    
    # Try TOTP first
    if user["totp_secret"] and verify_totp_code(user["totp_secret"], code):
        return True
    
    # Try backup codes
    if user["backup_codes"]:
        import hashlib
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        
        if code_hash in user["backup_codes"]:
            # Remove used backup code
            new_codes = [c for c in user["backup_codes"] if c != code_hash]
            await pool.execute(
                "UPDATE users SET backup_codes = $1 WHERE id = $2",
                new_codes, user_id
            )
            return True
    
    return False
