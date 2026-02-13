"""Authentication module."""

from .router import router
from .service import AuthService
from .dependencies import get_current_user, get_current_active_user
from .exceptions import (
    AuthenticationError,
    AuthorizationError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    RateLimitError
)

__all__ = [
    "router",
    "AuthService",
    "get_current_user",
    "get_current_active_user",
    "AuthenticationError",
    "AuthorizationError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidCredentialsError",
    "RateLimitError"
] 