"""Authentication service."""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import settings
from ..models import AuthAuditLog, FailedLoginAttempt, User
from . import schemas

# Password hashing with salt rounds = 10 for small system
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)

# JWT settings
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
RATE_LIMIT_ATTEMPTS = 5
RATE_LIMIT_WINDOW_MINUTES = 15


class AuthService:
    """Authentication service class."""

    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(
            User.username == username,
            User.is_deleted == False
        ).first()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(
            User.id == user_id,
            User.is_deleted == False
        ).first()

    def check_rate_limit(self, username: str, ip_address: str) -> bool:
        """Check if user is rate limited."""
        # Clean old attempts
        cutoff_time = datetime.utcnow() - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
        self.db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.last_attempt_at < cutoff_time
        ).delete()

        # Check existing attempts
        attempt = self.db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username,
            FailedLoginAttempt.ip_address == ip_address
        ).first()

        if attempt:
            if attempt.is_blocked and attempt.blocked_until and attempt.blocked_until > datetime.utcnow():
                return False  # Still blocked
            
            if attempt.attempt_count >= RATE_LIMIT_ATTEMPTS:
                # Block user
                attempt.is_blocked = True
                attempt.blocked_until = datetime.utcnow() + timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
                self.db.commit()
                return False

        return True

    def record_failed_attempt(self, username: str, ip_address: str):
        """Record failed login attempt."""
        attempt = self.db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username,
            FailedLoginAttempt.ip_address == ip_address
        ).first()

        if attempt:
            attempt.attempt_count += 1
            attempt.last_attempt_at = datetime.utcnow()
        else:
            attempt = FailedLoginAttempt(
                username=username,
                ip_address=ip_address,
                attempt_count=1
            )
            self.db.add(attempt)

        self.db.commit()

    def clear_failed_attempts(self, username: str, ip_address: str):
        """Clear failed login attempts for successful login."""
        self.db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.username == username,
            FailedLoginAttempt.ip_address == ip_address
        ).delete()
        self.db.commit()

    def log_auth_action(self, user_id: Optional[str], action: str, ip_address: str, 
                       user_agent: str, success: bool = True):
        """Log authentication action."""
        log = AuthAuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        self.db.add(log)
        self.db.commit()

    def authenticate_user(self, username: str, password: str, request: Request) -> Optional[User]:
        """Authenticate user with rate limiting."""
        # Get client IP
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        # Check rate limit
        if not self.check_rate_limit(username, ip_address):
            self.log_auth_action(None, "login_failed", ip_address, user_agent, False)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Tài khoản bị khóa tạm thời, vui lòng thử lại sau 15 phút"
            )

        # Get user
        user = self.get_user_by_username(username)
        if not user:
            self.record_failed_attempt(username, ip_address)
            self.log_auth_action(None, "login_failed", ip_address, user_agent, False)
            return None

        # Verify password
        if not self.verify_password(password, user.hashed_password):
            self.record_failed_attempt(username, ip_address)
            self.log_auth_action(str(user.id), "login_failed", ip_address, user_agent, False)
            return None

        # Check if user is active
        if not user.is_active:
            self.log_auth_action(str(user.id), "login_failed", ip_address, user_agent, False)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tài khoản đã bị vô hiệu hóa"
            )

        # Clear failed attempts on successful login
        self.clear_failed_attempts(username, ip_address)
        self.log_auth_action(str(user.id), "login", ip_address, user_agent, True)

        return user

    def login(self, login_data: schemas.LoginRequest, request: Request) -> schemas.LoginResponse:
        """Login user."""
        user = self.authenticate_user(login_data.username, login_data.password, request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tên đăng nhập hoặc mật khẩu không đúng"
            )

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username
        }

        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)

        return schemas.LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=schemas.UserResponse.from_orm(user)
        )

    def logout(self, refresh_token: str, request: Request):
        """Logout user."""
        # Verify refresh token
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        # Log logout action
        self.log_auth_action(user_id, "logout", ip_address, user_agent, True)

        return {"message": "Đăng xuất thành công"}

    def refresh_token(self, refresh_token: str) -> schemas.RefreshResponse:
        """Refresh access token."""
        payload = self.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user_id = payload.get("sub")
        user = self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        token_data = {
            "sub": str(user.id),
            "username": user.username
        }

        access_token = self.create_access_token(token_data)
        new_refresh_token = self.create_refresh_token(token_data)

        return schemas.RefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def create_user(self, user_data: schemas.UserCreate) -> schemas.UserResponse:
        """Create new user."""
        # Check if username exists
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username đã tồn tại"
            )

        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=user_data.is_active
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return schemas.UserResponse.from_orm(user)

    def register(self, register_data: schemas.RegisterRequest, request: Request) -> schemas.RegisterResponse:
        """Register new user with basic information."""
        # Get client IP for audit logging
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        # Check if username exists
        if self.get_user_by_username(register_data.username):
            # self.log_auth_action(None, "register_failed", ip_address, user_agent, False)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tên đăng nhập đã tồn tại"
            )

        # Create user with basic information
        hashed_password = self.get_password_hash(register_data.password)
        user = User(
            username=register_data.username,
            hashed_password=hashed_password,
            is_active=True
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Log successful registration
        # self.log_auth_action(str(user.id), "register", ip_address, user_agent, True)

        return schemas.RegisterResponse(
            message="Đăng ký thành công",
            user={
                "id": str(user.id),
                "username": user.username
            }
        ) 