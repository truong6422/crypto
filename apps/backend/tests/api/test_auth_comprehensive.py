"""Comprehensive API tests for authentication and user management."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from src.auth.models import User, Role, Permission
from src.core.security import create_access_token


class TestAuthenticationAPI:
    """Test authentication endpoints."""
    
    def test_login_success(self, client, sample_user):
        """Test successful login."""
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "testuser"
        assert data["user"]["email"] == "test@example.com"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post("/api/v1/auth/login", json={
            "username": "invaliduser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "Invalid credentials" in data["detail"]
    
    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        response = client.post("/api/v1/auth/login", json={
            "username": "testuser"
            # missing password
        })
        
        assert response.status_code == 422
    
    def test_login_empty_fields(self, client):
        """Test login with empty fields."""
        response = client.post("/api/v1/auth/login", json={
            "username": "",
            "password": ""
        })
        
        assert response.status_code == 422
    
    def test_login_inactive_user(self, client, db_session, sample_role):
        """Test login with inactive user."""
        # Create inactive user
        user = User(
            id="inactive-user-id",
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password="hashed_password",
            role_id=sample_role.id,
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post("/api/v1/auth/login", json={
            "username": "inactiveuser",
            "password": "testpassword123"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Inactive user" in data["detail"]


class TestUserManagementAPI:
    """Test user management endpoints."""
    
    def test_get_users_unauthorized(self, client):
        """Test getting users without authentication."""
        response = client.get("/api/v1/users")
        assert response.status_code == 401
    
    def test_get_users_success(self, client, admin_token):
        """Test getting users with admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
    
    def test_get_users_pagination(self, client, admin_token):
        """Test user pagination."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/users?page=1&size=5", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5
    
    def test_get_users_filter_by_role(self, client, admin_token, sample_role):
        """Test filtering users by role."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(f"/api/v1/users?role_id={sample_role.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        # Verify all returned users have the specified role
        for user in data["items"]:
            assert user["role_id"] == sample_role.id
    
    def test_get_users_search(self, client, admin_token):
        """Test searching users by username or email."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/users?search=test", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        # Verify search results contain "test"
        for user in data["items"]:
            assert "test" in user["username"].lower() or "test" in user["email"].lower()
    
    def test_create_user_success(self, client, admin_token, sample_role):
        """Test creating a new user."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "role_id": sample_role.id,
            "full_name": "New User"
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["role_id"] == sample_role.id
        assert data["full_name"] == "New User"
        assert "password" not in data  # Password should not be returned
    
    def test_create_user_duplicate_username(self, client, admin_token, sample_role, sample_user):
        """Test creating user with duplicate username."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "testuser",  # Duplicate username
            "email": "different@example.com",
            "password": "password123",
            "role_id": sample_role.id,
            "full_name": "Different User"
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "Username already exists" in data["detail"]
    
    def test_create_user_duplicate_email(self, client, admin_token, sample_role, sample_user):
        """Test creating user with duplicate email."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "differentuser",
            "email": "test@example.com",  # Duplicate email
            "password": "password123",
            "role_id": sample_role.id,
            "full_name": "Different User"
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "Email already exists" in data["detail"]
    
    def test_create_user_invalid_role(self, client, admin_token):
        """Test creating user with invalid role ID."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "role_id": "invalid-role-id",
            "full_name": "New User"
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "Role not found" in data["detail"]
    
    def test_update_user_success(self, client, admin_token, sample_user):
        """Test updating user information."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {
            "full_name": "Updated User Name",
            "email": "updated@example.com"
        }
        
        response = client.put(f"/api/v1/users/{sample_user.id}", 
                            json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated User Name"
        assert data["email"] == "updated@example.com"
    
    def test_update_user_not_found(self, client, admin_token):
        """Test updating non-existent user."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"full_name": "Updated Name"}
        
        response = client.put("/api/v1/users/non-existent-id", 
                            json=update_data, headers=headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]
    
    def test_delete_user_success(self, client, admin_token, sample_user):
        """Test deleting a user."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.delete(f"/api/v1/users/{sample_user.id}", headers=headers)
        
        assert response.status_code == 204
    
    def test_delete_user_not_found(self, client, admin_token):
        """Test deleting non-existent user."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.delete("/api/v1/users/non-existent-id", headers=headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]
    
    def test_toggle_user_status(self, client, admin_token, sample_user):
        """Test toggling user active status."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Toggle to inactive
        response = client.patch(f"/api/v1/users/{sample_user.id}/toggle-status", 
                              headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == False
        
        # Toggle back to active
        response = client.patch(f"/api/v1/users/{sample_user.id}/toggle-status", 
                              headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == True


class TestRoleManagementAPI:
    """Test role management endpoints."""
    
    def test_get_roles_unauthorized(self, client):
        """Test getting roles without authentication."""
        response = client.get("/api/v1/roles")
        assert response.status_code == 401
    
    def test_get_roles_success(self, client, admin_token):
        """Test getting roles with admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/roles", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_role_success(self, client, admin_token):
        """Test creating a new role."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        role_data = {
            "name": "new_role",
            "description": "A new test role"
        }
        
        response = client.post("/api/v1/roles", json=role_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new_role"
        assert data["description"] == "A new test role"
    
    def test_create_role_duplicate_name(self, client, admin_token, sample_role):
        """Test creating role with duplicate name."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        role_data = {
            "name": "test_role",  # Duplicate name
            "description": "Another test role"
        }
        
        response = client.post("/api/v1/roles", json=role_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "Role name already exists" in data["detail"]
    
    def test_update_role_success(self, client, admin_token, sample_role):
        """Test updating role information."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {
            "description": "Updated role description"
        }
        
        response = client.put(f"/api/v1/roles/{sample_role.id}", 
                            json=update_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated role description"
    
    def test_delete_role_success(self, client, admin_token, sample_role):
        """Test deleting a role."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.delete(f"/api/v1/roles/{sample_role.id}", headers=headers)
        
        assert response.status_code == 204


class TestPermissionManagementAPI:
    """Test permission management endpoints."""
    
    def test_get_permissions_unauthorized(self, client):
        """Test getting permissions without authentication."""
        response = client.get("/api/v1/permissions")
        assert response.status_code == 401
    
    def test_get_permissions_success(self, client, admin_token):
        """Test getting permissions with admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/permissions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_create_permission_success(self, client, admin_token):
        """Test creating a new permission."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        permission_data = {
            "name": "NEW_PERMISSION",
            "description": "A new test permission"
        }
        
        response = client.post("/api/v1/permissions", json=permission_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "NEW_PERMISSION"
        assert data["description"] == "A new test permission"
    
    def test_create_permission_duplicate_name(self, client, admin_token, db_session):
        """Test creating permission with duplicate name."""
        # Create a permission first
        permission = Permission(
            id="test-permission-id",
            name="DUPLICATE_PERMISSION",
            description="Test permission"
        )
        db_session.add(permission)
        db_session.commit()
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        permission_data = {
            "name": "DUPLICATE_PERMISSION",  # Duplicate name
            "description": "Another test permission"
        }
        
        response = client.post("/api/v1/permissions", json=permission_data, headers=headers)
        
        assert response.status_code == 400
        data = response.json()
        assert "Permission name already exists" in data["detail"]


class TestAuthorizationMiddleware:
    """Test authorization middleware and role-based access control."""
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/users")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/users", headers=headers)
        assert response.status_code == 401
    
    def test_admin_only_endpoint_with_user_token(self, client, test_user, sample_role):
        """Test accessing admin-only endpoint with regular user token."""
        # Create token for regular user
        token = create_access_token(data={"sub": test_user.username})
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/v1/roles", headers=headers)
        assert response.status_code == 403
    
    def test_admin_only_endpoint_with_admin_token(self, client, admin_token):
        """Test accessing admin-only endpoint with admin token."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v1/roles", headers=headers)
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_invalid_json_request(self, client, admin_token):
        """Test handling of invalid JSON in request body."""
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}
        response = client.post("/api/v1/users", data="invalid json", headers=headers)
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client, admin_token):
        """Test handling of missing required fields."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/v1/users", json={}, headers=headers)
        assert response.status_code == 422
    
    def test_invalid_email_format(self, client, admin_token, sample_role):
        """Test handling of invalid email format."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "testuser",
            "email": "invalid-email",  # Invalid email format
            "password": "password123",
            "role_id": sample_role.id,
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        assert response.status_code == 422
    
    def test_password_too_short(self, client, admin_token, sample_role):
        """Test handling of password that's too short."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",  # Too short
            "role_id": sample_role.id,
            "full_name": "Test User"
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        assert response.status_code == 422


class TestSecurityFeatures:
    """Test security features and best practices."""
    
    def test_password_not_returned_in_response(self, client, admin_token, sample_user):
        """Test that password is never returned in API responses."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(f"/api/v1/users/{sample_user.id}", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data
    
    def test_jwt_token_expiration(self, client, sample_user):
        """Test JWT token expiration handling."""
        # Create an expired token
        with patch('src.core.jwt.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2020, 1, 1)
            expired_token = create_access_token(data={"sub": sample_user.username})
        
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/users", headers=headers)
        
        assert response.status_code == 401
    
    def test_sql_injection_prevention(self, client, admin_token):
        """Test SQL injection prevention."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        # Try to inject SQL in search parameter
        response = client.get("/api/v1/users?search='; DROP TABLE users; --", headers=headers)
        
        # Should not crash and should handle gracefully
        assert response.status_code in [200, 400, 422]
    
    def test_xss_prevention(self, client, admin_token, sample_role):
        """Test XSS prevention in user input."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role_id": sample_role.id,
            "full_name": "<script>alert('xss')</script>"  # XSS attempt
        }
        
        response = client.post("/api/v1/users", json=user_data, headers=headers)
        
        # Should accept the input but not execute the script
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "<script>alert('xss')</script>"  # Should be escaped/stored as-is 