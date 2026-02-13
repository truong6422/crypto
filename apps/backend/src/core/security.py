"""Security utilities cho password hashing và verification."""

from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash password sử dụng bcrypt.
    
    Args:
        password: Password plain text
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password với hash.
    
    Args:
        plain_password: Password plain text
        hashed_password: Hashed password
        
    Returns:
        bool: True nếu password đúng
    """
    return pwd_context.verify(plain_password, hashed_password) 