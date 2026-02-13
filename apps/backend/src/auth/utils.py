"""Authentication utilities."""

import re
from typing import Optional


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự"
    
    if len(password) > 100:
        return False, "Mật khẩu không được quá 100 ký tự"
    
    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if len(username) < 3:
        return False, "Tên đăng nhập phải có ít nhất 3 ký tự"
    
    if len(username) > 100:
        return False, "Tên đăng nhập không được quá 100 ký tự"
    
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Tên đăng nhập chỉ được chứa chữ cái, số và dấu gạch dưới"
    
    return True, None


def sanitize_username(username: str) -> str:
    """
    Sanitize username by removing special characters.
    
    Args:
        username: Username to sanitize
        
    Returns:
        str: Sanitized username
    """
    # Remove special characters, keep only alphanumeric and underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '', username)
    return sanitized.lower()


def mask_email(email: str) -> str:
    """
    Mask email for privacy.
    
    Args:
        email: Email to mask
        
    Returns:
        str: Masked email
    """
    if '@' not in email:
        return email
    
    username, domain = email.split('@', 1)
    
    if len(username) <= 2:
        masked_username = username
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}" 