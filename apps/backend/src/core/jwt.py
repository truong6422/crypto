"""JWT token utilities."""

from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from ..config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Tạo JWT access token.
    
    Args:
        data: Data để encode vào token
        expires_delta: Thời gian hết hạn (optional)
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, remember_me: bool = False) -> str:
    """
    Tạo JWT refresh token.
    
    Args:
        data: Data để encode vào token
        remember_me: Có ghi nhớ đăng nhập không
        
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    if remember_me:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS_REMEMBER)
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify và decode JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        dict: Decoded payload
        
    Raises:
        jwt.JWTError: Nếu token không hợp lệ
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload


def verify_refresh_token(token: str) -> dict:
    """
    Verify và decode JWT refresh token.
    
    Args:
        token: JWT refresh token
        
    Returns:
        dict: Decoded payload
        
    Raises:
        jwt.JWTError: Nếu token không hợp lệ hoặc không phải refresh token
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("type") != "refresh":
        raise jwt.JWTError("Invalid token type")
    return payload 