"""Unit tests cho auth schemas."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.auth.schemas import (
    UserCreate, UserUpdate, UserResponse, UserResponseSimple, UserListResponse,
    RoleCreate, RoleUpdate, RoleResponse, RoleListResponse,
    PermissionCreate, PermissionUpdate, PermissionResponse, PermissionListResponse,
    LoginRequest, LoginResponse, TokenData
)
from src.constants import UserStatus


class TestUserSchemas:
    """Test cases cho User schemas."""

    def test_user_create_schema(self):
        """Test UserCreate schema."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpassword",
            "role_id": "test-role-id"
        }
        user_create = UserCreate(**user_data)
        
        assert user_create.username == "testuser"
        assert user_create.email == "test@example.com"
        assert user_create.full_name == "Test User"
        assert user_create.password == "testpassword"
        assert user_create.role_id == "test-role-id"

    def test_user_create_schema_validation(self):
        """Test UserCreate schema validation."""
        # Test thiếu required fields
        with pytest.raises(ValidationError):
            UserCreate(username="testuser")
        
        # Test email format không hợp lệ
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="invalid-email",
                full_name="Test User",
                password="testpassword",
                role_id="test-role-id"
            )

    def test_user_update_schema(self):
        """Test UserUpdate schema."""
        user_data = {
            "username": "newusername",
            "full_name": "New Name"
        }
        user_update = UserUpdate(**user_data)
        
        assert user_update.username == "newusername"
        assert user_update.full_name == "New Name"
        assert user_update.email is None
        assert user_update.role_id is None
        assert user_update.status is None

    def test_user_response_schema(self):
        """Test UserResponse schema."""
        role_data = {
            "id": "role-id",
            "name": "admin",
            "description": "Admin role",
            "is_active": True,
            "permissions": [],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None
        }
        
        user_data = {
            "id": "user-id",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "avatar_url": None,
            "role": role_data,
            "status": UserStatus.ACTIVE,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        user_response = UserResponse(**user_data)
        assert user_response.id == "user-id"
        assert user_response.username == "testuser"
        assert user_response.email == "test@example.com"
        assert user_response.full_name == "Test User"
        assert user_response.role.id == "role-id"
        assert user_response.status == UserStatus.ACTIVE

    def test_user_list_response_schema(self):
        """Test UserListResponse schema."""
        user1 = {
            "id": "user1",
            "username": "user1",
            "email": "user1@example.com",
            "full_name": "User 1",
            "avatar_url": None,
            "role": "admin",
            "status": "active",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        user2 = {
            "id": "user2",
            "username": "user2",
            "email": "user2@example.com",
            "full_name": "User 2",
            "avatar_url": None,
            "role": "user",
            "status": "active",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        list_data = {
            "items": [user1, user2],
            "total": 2,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
            "has_next": False,
            "has_prev": False
        }
        
        list_response = UserListResponse(**list_data)
        assert len(list_response.items) == 2
        assert list_response.total == 2
        assert list_response.page == 1
        assert list_response.page_size == 20
        assert list_response.total_pages == 1
        assert list_response.has_next is False
        assert list_response.has_prev is False


class TestRoleSchemas:
    """Test cases cho Role schemas."""

    def test_role_create_schema(self):
        """Test RoleCreate schema."""
        role_data = {
            "name": "admin",
            "description": "Administrator role",
            "is_active": True,
            "permission_ids": ["perm1", "perm2"]
        }
        role_create = RoleCreate(**role_data)
        
        assert role_create.name == "admin"
        assert role_create.description == "Administrator role"
        assert role_create.is_active is True
        assert role_create.permission_ids == ["perm1", "perm2"]

    def test_role_update_schema(self):
        """Test RoleUpdate schema."""
        role_data = {
            "name": "newadmin",
            "is_active": False
        }
        role_update = RoleUpdate(**role_data)
        
        assert role_update.name == "newadmin"
        assert role_update.is_active is False
        assert role_update.description is None
        assert role_update.permission_ids is None

    def test_role_response_schema(self):
        """Test RoleResponse schema."""
        permission_data = {
            "id": "perm-id",
            "name": "read_users",
            "description": "Read users permission",
            "is_active": True,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None
        }
        
        role_data = {
            "id": "role-id",
            "name": "admin",
            "description": "Admin role",
            "is_active": True,
            "permissions": [permission_data],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        role_response = RoleResponse(**role_data)
        assert role_response.id == "role-id"
        assert role_response.name == "admin"
        assert role_response.description == "Admin role"
        assert role_response.is_active is True
        assert len(role_response.permissions) == 1
        assert role_response.permissions[0].id == "perm-id"


class TestPermissionSchemas:
    """Test cases cho Permission schemas."""

    def test_permission_create_schema(self):
        """Test PermissionCreate schema."""
        permission_data = {
            "name": "read_users",
            "description": "Read users permission",
            "is_active": True
        }
        permission_create = PermissionCreate(**permission_data)
        
        assert permission_create.name == "read_users"
        assert permission_create.description == "Read users permission"
        assert permission_create.is_active is True

    def test_permission_update_schema(self):
        """Test PermissionUpdate schema."""
        permission_data = {
            "name": "write_users",
            "is_active": False
        }
        permission_update = PermissionUpdate(**permission_data)
        
        assert permission_update.name == "write_users"
        assert permission_update.is_active is False
        assert permission_update.description is None

    def test_permission_response_schema(self):
        """Test PermissionResponse schema."""
        permission_data = {
            "id": "perm-id",
            "name": "read_users",
            "description": "Read users permission",
            "is_active": True,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        permission_response = PermissionResponse(**permission_data)
        assert permission_response.id == "perm-id"
        assert permission_response.name == "read_users"
        assert permission_response.description == "Read users permission"
        assert permission_response.is_active is True


class TestAuthSchemas:
    """Test cases cho Auth schemas."""

    def test_login_request_schema(self):
        """Test LoginRequest schema."""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        login_request = LoginRequest(**login_data)
        
        assert login_request.username == "testuser"
        assert login_request.password == "testpassword"

    def test_login_response_schema(self):
        """Test LoginResponse schema."""
        role_data = {
            "id": "role-id",
            "name": "admin",
            "description": "Admin role",
            "is_active": True,
            "permissions": [],
            "created_at": "2023-01-01T00:00:00",
            "updated_at": None
        }
        
        user_data = {
            "id": "user-id",
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "avatar_url": None,
            "role": role_data,
            "status": UserStatus.ACTIVE,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        login_data = {
            "access_token": "test-token",
            "token_type": "bearer",
            "user": user_data
        }
        
        login_response = LoginResponse(**login_data)
        assert login_response.access_token == "test-token"
        assert login_response.token_type == "bearer"
        assert login_response.user.id == "user-id"
        assert login_response.user.username == "testuser"

    def test_token_data_schema(self):
        """Test TokenData schema."""
        token_data = TokenData(username="testuser", user_id="user-id")
        
        assert token_data.username == "testuser"
        assert token_data.user_id == "user-id"


class TestSchemaValidation:
    """Test cases cho schema validation."""

    def test_user_create_required_fields(self):
        """Test UserCreate required fields."""
        with pytest.raises(ValidationError):
            UserCreate(username="testuser")
        
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com")

    def test_role_create_required_fields(self):
        """Test RoleCreate required fields."""
        with pytest.raises(ValidationError):
            RoleCreate()

    def test_permission_create_required_fields(self):
        """Test PermissionCreate required fields."""
        with pytest.raises(ValidationError):
            PermissionCreate()

    def test_login_request_required_fields(self):
        """Test LoginRequest required fields."""
        with pytest.raises(ValidationError):
            LoginRequest(username="testuser")
        
        with pytest.raises(ValidationError):
            LoginRequest(password="testpassword") 