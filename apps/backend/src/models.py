"""Database models for authentication system."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from .constants import Gender

Base = declarative_base()


class User(Base):
    """User model with audit fields."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)  # Updated to 50 chars per story
    email = Column(String(255), unique=True, nullable=True)  # Made optional for basic registration
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)  # Made optional for basic registration
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)  # Admin flag
    avatar_url = Column(String(500), nullable=True)

    # Audit fields (complete)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    deleted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class AuthAuditLog(Base):
    """Authentication audit log model."""
    __tablename__ = "auth_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)  # 'login', 'logout', 'login_failed', 'register'
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", backref="auth_logs")

    def __repr__(self):
        return f"<AuthAuditLog(id={self.id}, action='{self.action}', success={self.success})>"


class FailedLoginAttempt(Base):
    """Failed login attempts tracking model."""
    __tablename__ = "failed_login_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    attempt_count = Column(Integer, default=1, nullable=False)
    first_attempt_at = Column(DateTime, default=func.now(), nullable=False)
    last_attempt_at = Column(DateTime, default=func.now(), nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    blocked_until = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<FailedLoginAttempt(username='{self.username}', attempts={self.attempt_count}, blocked={self.is_blocked})>"


class UserProfile(Base):
    """User profile model for additional user information."""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Profile information
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)  # Uses Gender enum values
    
    # Preferences
    # Preferences
    preferences = Column(Text, nullable=True)  # JSON string for user preferences
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationship
    user = relationship("User", backref="profile", uselist=False)
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>" 