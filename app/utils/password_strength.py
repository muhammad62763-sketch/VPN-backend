"""Password strength validation utilities"""
import re
from typing import Tuple

def check_password_strength(password: str) -> Tuple[bool, str, int]:
    """
    Check password strength and return (is_valid, message, score)
    Score: 0-100
    """
    score = 0
    issues = []
    
    # Length check
    length = len(password)
    if length < 12:
        issues.append("Password must be at least 12 characters")
        return False, "; ".join(issues), 0
    elif length >= 12:
        score += 20
    if length >= 16:
        score += 10
    if length >= 20:
        score += 10
    
    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 15
    else:
        issues.append("Add lowercase letters")
    
    if re.search(r'[A-Z]', password):
        score += 15
    else:
        issues.append("Add uppercase letters")
    
    if re.search(r'\d', password):
        score += 15
    else:
        issues.append("Add numbers")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 15
    else:
        issues.append("Add special characters")
    
    # Complexity checks
    if not re.search(r'(.)\1{2,}', password):  # No 3+ repeated chars
        score += 10
    
    # Common patterns check
    common_patterns = ['123', 'abc', 'password', 'qwerty', '111']
    if not any(pattern in password.lower() for pattern in common_patterns):
        score += 10
    else:
        issues.append("Avoid common patterns")
    
    is_valid = score >= 60 and len(issues) == 0
    message = "Strong password" if is_valid else "; ".join(issues)
    
    return is_valid, message, min(score, 100)

def get_password_requirements() -> dict:
    """Return password requirements"""
    return {
        "min_length": 12,
        "require_lowercase": True,
        "require_uppercase": True,
        "require_numbers": True,
        "require_special": True,
        "no_common_patterns": True
    }
