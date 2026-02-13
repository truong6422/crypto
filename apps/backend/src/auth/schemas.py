"""Authentication schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_serializer, field_validator

from ..constants import Gender


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)  # Updated to 50 chars per story
    email: Optional[EmailStr] = None  # Made optional for basic registration
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)  # Made optional for basic registration
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=6, max_length=50)  # Updated to 50 chars per story


class RegisterRequest(BaseModel):
    """Schema for basic registration request."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=50)
    confirm_password: str = Field(..., min_length=6, max_length=50)

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Mật khẩu xác nhận không khớp')
        return v


class RegisterResponse(BaseModel):
    """Schema for registration response."""
    message: str = "Đăng ký thành công"
    user: dict

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=100)
    remember_me: Optional[bool] = False


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class LogoutRequest(BaseModel):
    """Schema for logout request."""
    refresh_token: str


class RefreshRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class RefreshResponse(BaseModel):
    """Schema for refresh token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthAuditLogResponse(BaseModel):
    """Schema for auth audit log response."""
    id: UUID
    user_id: Optional[UUID] = None
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


class FailedLoginAttemptResponse(BaseModel):
    """Schema for failed login attempt response."""
    id: UUID
    username: str
    ip_address: Optional[str] = None
    attempt_count: int
    first_attempt_at: datetime
    last_attempt_at: datetime
    is_blocked: bool
    blocked_until: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfileCreate(BaseModel):
    """Schema for creating user profile."""
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=20)
    preferences: Optional[str] = None
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        """Validate gender value against Gender enum."""
        if v is None:
            return v
        valid_genders = [g.value for g in Gender]
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of: {', '.join(valid_genders)}")
        return v


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = Field(None, max_length=20)
    preferences: Optional[str] = None
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        """Validate gender value against Gender enum."""
        if v is None:
            return v
        valid_genders = [g.value for g in Gender]
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of: {', '.join(valid_genders)}")
        return v


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""
    id: UUID
    user_id: UUID
    phone: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    preferences: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True