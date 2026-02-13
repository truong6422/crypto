"""Comprehensive tests for authentication models."""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.auth.models import User, Role, Permission, RolePermission
from src.core.security import get_password_hash, verify_password


class TestUserModel:
    """Test User model functionality."""
    
    def test_create_user_success(self, db_session, sample_role):
        """Test creating a user successfully."""
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            role_id=sample_role.id,
            full_name="Test User",
            avatar_url=None,
            is_active=True
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id == "test-user-id"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active == True
        assert user.role_id == sample_role.id
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_unique_username_constraint(self, db_session, sample_role, sample_user):
        """Test that username must be unique."""
        duplicate_user = User(
            id="duplicate-user-id",
            username="testuser",  # Same username as sample_user
            email="different@example.com",
            hashed_password=get_password_hash("password123"),
            role_id=sample_role.id,
            full_name="Duplicate User"
        )
        
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_unique_email_constraint(self, db_session, sample_role, sample_user):
        """Test that email must be unique."""
        duplicate_user = User(
            id="duplicate-user-id",
            username="differentuser",
            email="test@example.com",  # Same email as sample_user
            hashed_password=get_password_hash("password123"),
            role_id=sample_role.id,
            full_name="Duplicate User"
        )
        
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        # Test without username
        user_no_username = User(
            id="test-id",
            email="test@example.com",
            hashed_password="hashed_password",
            role_id="role-id"
        )
        
        db_session.add(user_no_username)
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Test without email
        user_no_email = User(
            id="test-id",
            username="testuser",
            hashed_password="hashed_password",
            role_id="role-id"
        )
        
        db_session.add(user_no_email)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_default_values(self, db_session, sample_role):
        """Test default values for user fields."""
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            role_id=sample_role.id
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_active == True
        assert user.avatar_url is None
        assert user.full_name is None
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_password_verification(self, db_session, sample_role):
        """Test password hashing and verification."""
        password = "testpassword123"
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash(password),
            role_id=sample_role.id
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify correct password
        assert verify_password(password, user.hashed_password) == True
        
        # Verify incorrect password
        assert verify_password("wrongpassword", user.hashed_password) == False
    
    def test_user_relationship_with_role(self, db_session, sample_role):
        """Test user relationship with role."""
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            role_id=sample_role.id
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Test relationship
        assert user.role.id == sample_role.id
        assert user.role.name == sample_role.name
    
    def test_user_string_representation(self, db_session, sample_role):
        """Test user string representation."""
        user = User(
            id="test-user-id",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            role_id=sample_role.id,
            full_name="Test User"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert str(user) == "User(id=test-user-id, username=testuser, email=test@example.com)"
        assert repr(user) == "User(id=test-user-id, username=testuser, email=test@example.com)"


class TestRoleModel:
    """Test Role model functionality."""
    
    def test_create_role_success(self, db_session):
        """Test creating a role successfully."""
        role = Role(
            id="test-role-id",
            name="test_role",
            description="Test role description"
        )
        
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        assert role.id == "test-role-id"
        assert role.name == "test_role"
        assert role.description == "Test role description"
        assert role.is_active == True
        assert role.created_at is not None
        assert role.updated_at is not None
    
    def test_role_unique_name_constraint(self, db_session, sample_role):
        """Test that role name must be unique."""
        duplicate_role = Role(
            id="duplicate-role-id",
            name="test_role",  # Same name as sample_role
            description="Different description"
        )
        
        db_session.add(duplicate_role)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_role_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        # Test without name
        role_no_name = Role(
            id="test-id",
            description="Test description"
        )
        
        db_session.add(role_no_name)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_role_default_values(self, db_session):
        """Test default values for role fields."""
        role = Role(
            id="test-role-id",
            name="test_role"
        )
        
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        assert role.is_active == True
        assert role.description is None
        assert role.created_at is not None
        assert role.updated_at is not None
    
    def test_role_relationship_with_users(self, db_session, sample_role):
        """Test role relationship with users."""
        user1 = User(
            id="user1-id",
            username="user1",
            email="user1@example.com",
            hashed_password="hashed_password",
            role_id=sample_role.id
        )
        
        user2 = User(
            id="user2-id",
            username="user2",
            email="user2@example.com",
            hashed_password="hashed_password",
            role_id=sample_role.id
        )
        
        db_session.add_all([user1, user2])
        db_session.commit()
        db_session.refresh(sample_role)
        
        # Test relationship
        assert len(sample_role.users) == 2
        assert user1 in sample_role.users
        assert user2 in sample_role.users
    
    def test_role_relationship_with_permissions(self, db_session):
        """Test role relationship with permissions."""
        role = Role(
            id="test-role-id",
            name="test_role"
        )
        
        permission1 = Permission(
            id="perm1-id",
            name="PERMISSION_1",
            description="First permission"
        )
        
        permission2 = Permission(
            id="perm2-id",
            name="PERMISSION_2",
            description="Second permission"
        )
        
        db_session.add_all([role, permission1, permission2])
        db_session.commit()
        
        # Add permissions to role
        role.permissions.append(permission1)
        role.permissions.append(permission2)
        db_session.commit()
        db_session.refresh(role)
        
        # Test relationship
        assert len(role.permissions) == 2
        assert permission1 in role.permissions
        assert permission2 in role.permissions
    
    def test_role_string_representation(self, db_session):
        """Test role string representation."""
        role = Role(
            id="test-role-id",
            name="test_role",
            description="Test role description"
        )
        
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        assert str(role) == "Role(id=test-role-id, name=test_role)"
        assert repr(role) == "Role(id=test-role-id, name=test_role)"


class TestPermissionModel:
    """Test Permission model functionality."""
    
    def test_create_permission_success(self, db_session):
        """Test creating a permission successfully."""
        permission = Permission(
            id="test-permission-id",
            name="TEST_PERMISSION",
            description="Test permission description"
        )
        
        db_session.add(permission)
        db_session.commit()
        db_session.refresh(permission)
        
        assert permission.id == "test-permission-id"
        assert permission.name == "TEST_PERMISSION"
        assert permission.description == "Test permission description"
        assert permission.is_active == True
        assert permission.created_at is not None
        assert permission.updated_at is not None
    
    def test_permission_unique_name_constraint(self, db_session):
        """Test that permission name must be unique."""
        permission1 = Permission(
            id="perm1-id",
            name="TEST_PERMISSION",
            description="First permission"
        )
        
        permission2 = Permission(
            id="perm2-id",
            name="TEST_PERMISSION",  # Same name
            description="Second permission"
        )
        
        db_session.add(permission1)
        db_session.commit()
        
        db_session.add(permission2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_permission_required_fields(self, db_session):
        """Test that required fields cannot be null."""
        # Test without name
        permission_no_name = Permission(
            id="test-id",
            description="Test description"
        )
        
        db_session.add(permission_no_name)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_permission_default_values(self, db_session):
        """Test default values for permission fields."""
        permission = Permission(
            id="test-permission-id",
            name="TEST_PERMISSION"
        )
        
        db_session.add(permission)
        db_session.commit()
        db_session.refresh(permission)
        
        assert permission.is_active == True
        assert permission.description is None
        assert permission.created_at is not None
        assert permission.updated_at is not None
    
    def test_permission_relationship_with_roles(self, db_session):
        """Test permission relationship with roles."""
        permission = Permission(
            id="test-permission-id",
            name="TEST_PERMISSION"
        )
        
        role1 = Role(
            id="role1-id",
            name="role1"
        )
        
        role2 = Role(
            id="role2-id",
            name="role2"
        )
        
        db_session.add_all([permission, role1, role2])
        db_session.commit()
        
        # Add permission to roles
        role1.permissions.append(permission)
        role2.permissions.append(permission)
        db_session.commit()
        db_session.refresh(permission)
        
        # Test relationship
        assert len(permission.roles) == 2
        assert role1 in permission.roles
        assert role2 in permission.roles
    
    def test_permission_string_representation(self, db_session):
        """Test permission string representation."""
        permission = Permission(
            id="test-permission-id",
            name="TEST_PERMISSION",
            description="Test permission description"
        )
        
        db_session.add(permission)
        db_session.commit()
        db_session.refresh(permission)
        
        assert str(permission) == "Permission(id=test-permission-id, name=TEST_PERMISSION)"
        assert repr(permission) == "Permission(id=test-permission-id, name=TEST_PERMISSION)"


class TestRolePermissionModel:
    """Test RolePermission model functionality."""
    
    def test_create_role_permission_success(self, db_session):
        """Test creating a role-permission relationship successfully."""
        role = Role(
            id="test-role-id",
            name="test_role"
        )
        
        permission = Permission(
            id="test-permission-id",
            name="TEST_PERMISSION"
        )
        
        db_session.add_all([role, permission])
        db_session.commit()
        
        # Create relationship
        role_permission = RolePermission(
            role_id=role.id,
            permission_id=permission.id
        )
        
        db_session.add(role_permission)
        db_session.commit()
        
        assert role_permission.role_id == role.id
        assert role_permission.permission_id == permission.id
        assert role_permission.created_at is not None
    
    def test_role_permission_unique_constraint(self, db_session):
        """Test that role-permission combination must be unique."""
        role = Role(
            id="test-role-id",
            name="test_role"
        )
        
        permission = Permission(
            id="test-permission-id",
            name="TEST_PERMISSION"
        )
        
        db_session.add_all([role, permission])
        db_session.commit()
        
        # Create first relationship
        role_permission1 = RolePermission(
            role_id=role.id,
            permission_id=permission.id
        )
        
        db_session.add(role_permission1)
        db_session.commit()
        
        # Try to create duplicate relationship
        role_permission2 = RolePermission(
            role_id=role.id,
            permission_id=permission.id
        )
        
        db_session.add(role_permission2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_role_permission_foreign_key_constraints(self, db_session):
        """Test foreign key constraints."""
        # Try to create relationship with non-existent role
        role_permission = RolePermission(
            role_id="non-existent-role-id",
            permission_id="non-existent-permission-id"
        )
        
        db_session.add(role_permission)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestModelRelationships:
    """Test complex relationships between models."""
    
    def test_user_role_permission_chain(self, db_session):
        """Test the complete chain: User -> Role -> Permission."""
        # Create permissions
        perm1 = Permission(id="perm1", name="READ_USERS")
        perm2 = Permission(id="perm2", name="WRITE_USERS")
        
        # Create role with permissions
        role = Role(id="admin-role", name="admin")
        role.permissions.extend([perm1, perm2])
        
        # Create user with role
        user = User(
            id="admin-user",
            username="admin",
            email="admin@example.com",
            hashed_password="hashed_password",
            role_id=role.id
        )
        
        db_session.add_all([perm1, perm2, role, user])
        db_session.commit()
        db_session.refresh(user)
        db_session.refresh(role)
        
        # Test relationships
        assert user.role == role
        assert role in user.role.permissions
        assert perm1 in user.role.permissions
        assert perm2 in user.role.permissions
        assert user in role.users
    
    def test_cascade_delete_role(self, db_session):
        """Test cascade delete when role is deleted."""
        # Create role with users and permissions
        role = Role(id="test-role", name="test_role")
        permission = Permission(id="test-perm", name="TEST_PERM")
        role.permissions.append(permission)
        
        user = User(
            id="test-user",
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password",
            role_id=role.id
        )
        
        db_session.add_all([role, permission, user])
        db_session.commit()
        
        # Delete role
        db_session.delete(role)
        db_session.commit()
        
        # Check that role-permission relationships are deleted
        role_permissions = db_session.query(RolePermission).filter_by(role_id=role.id).all()
        assert len(role_permissions) == 0
        
        # Check that users are not deleted (should be handled by application logic)
        users = db_session.query(User).filter_by(role_id=role.id).all()
        assert len(users) == 1  # User still exists but with invalid role_id
    
    def test_cascade_delete_permission(self, db_session):
        """Test cascade delete when permission is deleted."""
        # Create permission with roles
        permission = Permission(id="test-perm", name="TEST_PERM")
        role1 = Role(id="role1", name="role1")
        role2 = Role(id="role2", name="role2")
        
        role1.permissions.append(permission)
        role2.permissions.append(permission)
        
        db_session.add_all([permission, role1, role2])
        db_session.commit()
        
        # Delete permission
        db_session.delete(permission)
        db_session.commit()
        
        # Check that role-permission relationships are deleted
        role_permissions = db_session.query(RolePermission).filter_by(permission_id=permission.id).all()
        assert len(role_permissions) == 0 