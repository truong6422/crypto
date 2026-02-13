"""Constants toàn cục cho ứng dụng."""

import enum
from typing import Dict, Any

# Enums
class UserRole(enum.Enum):
    """Enumeration vai trò người dùng."""
    ADMIN = "admin"
    USER = "user"
    STAFF = "staff"


class UserStatus(enum.Enum):
    """Enumeration trạng thái người dùng."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class Gender(enum.Enum):
    """Enumeration giới tính."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class AuditEventType(enum.Enum):
    """Enumeration loại sự kiện audit."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    REFRESH_TOKEN = "refresh_token"
    TOKEN_EXPIRED = "token_expired"


# Message constants
class Messages:
    """Constants cho các message text."""
    
    # Auth messages
    AUTH_INVALID_CREDENTIALS = "auth.invalid_credentials"
    AUTH_USER_NOT_FOUND = "auth.user_not_found"
    AUTH_USER_INACTIVE = "auth.user_inactive"
    AUTH_USER_ALREADY_EXISTS = "auth.user_already_exists"
    AUTH_USERNAME_ALREADY_EXISTS = "auth.username_already_exists"
    AUTH_EMAIL_ALREADY_EXISTS = "auth.email_already_exists"
    AUTH_INVALID_TOKEN = "auth.invalid_token"
    AUTH_INSUFFICIENT_PERMISSIONS = "auth.insufficient_permissions"
    
    # User messages
    USER_CREATED_SUCCESS = "user.created_success"
    USER_UPDATED_SUCCESS = "user.updated_success"
    USER_DELETED_SUCCESS = "user.deleted_success"
    USER_NOT_FOUND = "user.not_found"
    USER_STATUS_UPDATED_SUCCESS = "user.status_updated_success"
    
    # Role messages
    ROLE_CREATED_SUCCESS = "role.created_success"
    ROLE_UPDATED_SUCCESS = "role.updated_success"
    ROLE_DELETED_SUCCESS = "role.deleted_success"
    ROLE_NOT_FOUND = "role.not_found"
    ROLE_ALREADY_EXISTS = "role.already_exists"
    
    # Validation messages
    VALIDATION_REQUIRED_FIELD = "validation.required_field"
    VALIDATION_INVALID_EMAIL = "validation.invalid_email"
    VALIDATION_PASSWORD_TOO_SHORT = "validation.password_too_short"
    VALIDATION_PASSWORD_TOO_WEAK = "validation.password_too_weak"
    
    # System messages
    SYSTEM_ERROR = "system.error"
    SYSTEM_SUCCESS = "system.success"
    SYSTEM_WARNING = "system.warning"


# Configuration constants
class Config:
    """Constants cho cấu hình."""
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Password
    MIN_PASSWORD_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # File upload
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword"]
    
    # Cache
    CACHE_TTL = 3600  # 1 hour
    CACHE_PREFIX = "crypto_project"
    
    # API
    API_VERSION = "v1"
    API_PREFIX = f"/api/{API_VERSION}"
    
    # Locale
    DEFAULT_LOCALE = "vi"
    SUPPORTED_LOCALES = ["vi", "en", "fr"]
    LOCALE_PATH = "locales" 