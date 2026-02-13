"""Database models cho module xác thực."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from ..models import Base, User, AuthAuditLog, FailedLoginAttempt

# Re-export models from src.models for backward compatibility
__all__ = ['User', 'AuthAuditLog', 'FailedLoginAttempt'] 