"""Unit tests cho auth models."""

import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from src.auth.models import User, Role, Permission
from src.constants import UserStatus


class TestUserModel:
    """Test cases cho User model."""

    def test_user_creation(self, db_session):
        """Test tạo user mới."""
        role = Role(name="test_role", description="Test role")
        db_session.add(role)
        db_session.commit()
        
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.hashed_password == "hashed_password"
        assert user.role_id == role.id
        assert user.status == UserStatus.ACTIVE

    def test_user_default_values(self, db_session):
        """Test giá trị mặc định của user."""
        role = Role(name="test_role", description="Test role")
        db_session.add(role)
        db_session.commit()
        
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.status == UserStatus.ACTIVE
        assert user.avatar_url is None
        assert user.created_at is not None
        # updated_at is only set on update, not creation
        assert user.updated_at is None

    def test_user_relationship(self, db_session):
        """Test relationship giữa User và Role."""
        role = Role(name="test_role", description="Test role")
        db_session.add(role)
        db_session.commit()
        
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.role_obj == role
        assert user in role.users


class TestRoleModel:
    """Test cases cho Role model."""

    def test_role_creation(self, db_session):
        """Test tạo role mới."""
        role = Role(
            name="admin",
            description="Administrator role"
        )
        db_session.add(role)
        db_session.commit()
        
        assert role.id is not None
        assert role.name == "admin"
        assert role.description == "Administrator role"

    def test_role_default_values(self, db_session):
        """Test giá trị mặc định của role."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.commit()
        
        assert role.is_active is True
        assert role.created_at is not None
        # updated_at is only set on update, not creation
        assert role.updated_at is None

    def test_role_permissions_relationship(self, db_session):
        """Test relationship giữa Role và Permission."""
        role = Role(name="test_role")
        permission = Permission(name="test_permission")
        
        db_session.add(role)
        db_session.add(permission)
        db_session.commit()
        
        role.permissions.append(permission)
        db_session.commit()
        
        assert permission in role.permissions
        assert role in permission.roles


class TestPermissionModel:
    """Test cases cho Permission model."""

    def test_permission_creation(self, db_session):
        """Test tạo permission mới."""
        permission = Permission(
            name="read_users",
            description="Can read user data"
        )
        db_session.add(permission)
        db_session.commit()
        
        assert permission.id is not None
        assert permission.name == "read_users"
        assert permission.description == "Can read user data"

    def test_permission_default_values(self, db_session):
        """Test giá trị mặc định của permission."""
        permission = Permission(name="test_permission")
        db_session.add(permission)
        db_session.commit()
        
        assert permission.is_active is True
        assert permission.created_at is not None
        # updated_at is only set on update, not creation
        assert permission.updated_at is None

    def test_permission_roles_relationship(self, db_session):
        """Test relationship giữa Permission và Role."""
        role = Role(name="test_role")
        permission = Permission(name="test_permission")
        
        db_session.add(role)
        db_session.add(permission)
        db_session.commit()
        
        permission.roles.append(role)
        db_session.commit()
        
        assert role in permission.roles
        assert permission in role.permissions


class TestRolePermissionRelationship:
    """Test cases cho relationship giữa Role và Permission."""

    def test_role_permissions_relationship(self, db_session):
        """Test many-to-many relationship."""
        role = Role(name="admin")
        permission1 = Permission(name="read_users")
        permission2 = Permission(name="write_users")
        
        db_session.add_all([role, permission1, permission2])
        db_session.commit()
        
        role.permissions.extend([permission1, permission2])
        db_session.commit()
        
        assert len(role.permissions) == 2
        assert permission1 in role.permissions
        assert permission2 in role.permissions
        assert role in permission1.roles
        assert role in permission2.roles


class TestModelValidation:
    """Test cases cho model validation."""

    def test_user_required_fields(self, db_session):
        """Test required fields của User."""
        # Test thiếu required fields
        with pytest.raises(IntegrityError):
            user = User()  # Thiếu required fields
            db_session.add(user)
            db_session.commit()

    def test_role_required_fields(self, db_session):
        """Test required fields của Role."""
        # Test thiếu required fields
        with pytest.raises(IntegrityError):
            role = Role()  # Thiếu required fields
            db_session.add(role)
            db_session.commit()

    def test_permission_required_fields(self, db_session):
        """Test required fields của Permission."""
        # Test thiếu required fields
        with pytest.raises(IntegrityError):
            permission = Permission()  # Thiếu required fields
            db_session.add(permission)
            db_session.commit()

    def test_user_email_format(self, db_session):
        """Test email format validation."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.commit()
        
        # Email format sẽ được validate ở application level
        user = User(
            username="testuser",
            email="invalid-email",  # Invalid format
            full_name="Test User",
            hashed_password="hashed_password",
            role_id=role.id
        )
        db_session.add(user)
        # SQLAlchemy không validate email format, chỉ unique constraint
        db_session.commit()
        assert user.email == "invalid-email"

    def test_user_status_validation(self, db_session):
        """Test user status validation."""
        role = Role(name="test_role")
        db_session.add(role)
        db_session.commit()
        
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role_id=role.id,
            status=UserStatus.INACTIVE
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.status == UserStatus.INACTIVE 