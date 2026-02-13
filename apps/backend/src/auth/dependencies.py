"""Authentication dependencies."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from .service import AuthService
from .exceptions import AuthorizationError as InsufficientPermissionsError

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Dependency để kiểm tra user có quyền admin.
    
    Args:
        current_user: User object hiện tại
        
    Returns:
        User: User object nếu là admin
        
    Raises:
        InsufficientPermissionsError: Nếu không phải admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập"
        )
    return current_user


def require_role(required_role: str):
    """
    Dependency để kiểm tra role người dùng.
    
    Args:
        required_role: Tên role yêu cầu
        
    Returns:
        function: Dependency function
    """
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if not current_user.role_obj or current_user.role_obj.name != required_role:
            # Admin có thể truy cập tất cả
            if not current_user.role_obj or current_user.role_obj.name != "admin":
                raise InsufficientPermissionsError(f"Yêu cầu quyền {required_role}")
        return current_user
    return role_checker


def require_permission(required_permission: str):
    """
    Dependency để kiểm tra permission của user.
    
    Args:
        required_permission: Tên permission yêu cầu
        
    Returns:
        function: Dependency function
    """
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        # Admin có tất cả quyền
        if current_user.role_obj and current_user.role_obj.name == "admin":
            return current_user
        
        # Kiểm tra permission trong role
        if current_user.role_obj:
            user_permissions = [perm.name for perm in current_user.role_obj.permissions]
            if required_permission not in user_permissions:
                raise InsufficientPermissionsError(f"Yêu cầu quyền {required_permission}")
        else:
            raise InsufficientPermissionsError(f"Yêu cầu quyền {required_permission}")
        
        return current_user
    return permission_checker


def get_user_by_id(user_id: str, db: Session = Depends(get_db)) -> Optional[User]:
    """
    Dependency để lấy user theo ID.
    
    Args:
        user_id: ID người dùng
        db: Database session
        
    Returns:
        Optional[User]: User object hoặc None
    """
    return db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()


 