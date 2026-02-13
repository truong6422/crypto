"""Integration tests cho auth API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from src.main import app
from tests.conftest import TestUser
from src.core.security import get_password_hash
from src.database import get_db
import uuid


class TestAuthAPI:
    """Test cases cho authentication API endpoints."""

    def test_login_success(self, client, sample_user):
        """Test login thành công."""
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_login_invalid_credentials(self, client):
        """Test login với thông tin không đúng."""
        login_data = {
            "username": "wronguser",
            "password": "wrongpassword"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_inactive_user(self, client, db_session):
        """Test login với user không active."""
        # Tạo user không active
        user = TestUser(
            username="inactiveuser",
            email="inactive@example.com",
            full_name="Inactive User",
            hashed_password=get_password_hash("testpassword123"),
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        login_data = {
            "username": "inactiveuser",
            "password": "testpassword123"
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 400

    def test_login_missing_fields(self, client):
        """Test login thiếu fields."""
        # Thiếu password
        login_data = {"username": "testuser"}
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422
        
        # Thiếu username
        login_data = {"password": "testpassword123"}
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 422

    def test_get_current_user_success(self, client, sample_user):
        """Test get current user thành công."""
        # Login để lấy token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test get current user
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()

    def test_get_current_user_invalid_token(self, client):
        """Test get current user với token không hợp lệ."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/me", headers=headers)
        
        assert response.status_code == 401

    def test_get_current_user_no_token(self, client):
        """Test get current user không có token."""
        response = client.get("/api/me")
        
        assert response.status_code == 403

    def test_get_current_user_expired_token(self, client):
        """Test get current user với token hết hạn."""
        # Tạo expired token
        with patch('src.core.jwt.create_access_token') as mock_create_token:
            mock_create_token.return_value = "expired-token"
            
            headers = {"Authorization": "Bearer expired-token"}
            response = client.get("/api/me", headers=headers)
            
            assert response.status_code == 401

    def test_refresh_token_success(self, client, sample_user):
        """Test refresh token thành công."""
        # Login để lấy token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test refresh token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/refresh", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid_token(self, client):
        """Test refresh token với token không hợp lệ."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.post("/api/auth/refresh", headers=headers)
        
        assert response.status_code == 401

    def test_logout_success(self, client, sample_user):
        """Test logout thành công."""
        # Login để lấy token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test logout
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/logout", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_logout_no_token(self, client):
        """Test logout không có token."""
        response = client.post("/api/auth/logout")
        
        assert response.status_code == 403

    def test_change_password_success(self, client, sample_user):
        """Test change password thành công."""
        # Login để lấy token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test change password
        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/change-password", json=change_data, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_change_password_wrong_current_password(self, client, sample_user):
        """Test change password với current password sai."""
        # Login để lấy token
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        
        # Test change password với wrong current password
        change_data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post("/api/auth/change-password", json=change_data, headers=headers)
        
        assert response.status_code == 400

    def test_change_password_no_token(self, client):
        """Test change password không có token."""
        change_data = {
            "current_password": "testpassword123",
            "new_password": "newpassword123"
        }
        response = client.post("/api/auth/change-password", json=change_data)
        
        assert response.status_code == 403

    def test_forgot_password_success(self, client, sample_user):
        """Test forgot password thành công."""
        forgot_data = {"email": "test@example.com"}
        response = client.post("/api/auth/forgot-password", json=forgot_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_forgot_password_email_not_found(self, client):
        """Test forgot password với email không tồn tại."""
        forgot_data = {"email": "nonexistent@example.com"}
        response = client.post("/api/auth/forgot-password", json=forgot_data)
        
        assert response.status_code == 404

    def test_reset_password_success(self, client, sample_user):
        """Test reset password thành công."""
        reset_data = {
            "token": "valid-reset-token",
            "new_password": "newpassword123"
        }
        response = client.post("/api/auth/reset-password", json=reset_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_reset_password_invalid_token(self, client):
        """Test reset password với token không hợp lệ."""
        response = client.post("/api/auth/reset-password", json={
            "token": "invalid-token",
            "new_password": "newpassword123"
        })
        assert response.status_code == 400
        assert "Invalid token" in response.json()["detail"]

    def test_update_user_permissions_success(self, client, admin_token, test_user, db_session):
        """Test cập nhật permissions cho user thành công."""
        # Tạo permissions test
        permission1 = Permission(
            id=str(uuid.uuid4()),
            name="test_permission_1",
            description="Test permission 1",
            is_active=True
        )
        permission2 = Permission(
            id=str(uuid.uuid4()),
            name="test_permission_2", 
            description="Test permission 2",
            is_active=True
        )
        
        db_session.add(permission1)
        db_session.add(permission2)
        db_session.commit()
        
        response = client.put(
            f"/api/v1/users/{test_user.id}/permissions",
            json=[permission1.id, permission2.id],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        # Kiểm tra user được cập nhật thành công
        assert data["username"] == test_user.username

    def test_update_user_permissions_user_not_found(self, client, admin_token):
        """Test cập nhật permissions cho user không tồn tại."""
        response = client.put(
            "/api/v1/users/non-existent-id/permissions",
            json=["permission1", "permission2"],
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 404
        assert "user.not_found" in response.json()["detail"]

    # Register endpoint tests
    def test_register_success(self, client):
        """Test đăng ký thành công."""
        register_data = {
            "username": "newuser",
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Đăng ký thành công"
        assert "user" in data
        assert data["user"]["username"] == "newuser"
        assert "id" in data["user"]

    def test_register_username_exists(self, client, sample_user):
        """Test đăng ký với username đã tồn tại."""
        register_data = {
            "username": "testuser",  # Username đã tồn tại từ sample_user
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Tên đăng nhập đã tồn tại" in data["detail"]

    def test_register_password_mismatch(self, client):
        """Test đăng ký với mật khẩu không khớp."""
        register_data = {
            "username": "newuser",
            "password": "newpassword123",
            "confirm_password": "differentpassword"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "Mật khẩu xác nhận không khớp" in str(data)

    def test_register_username_too_short(self, client):
        """Test đăng ký với username quá ngắn."""
        register_data = {
            "username": "ab",  # Dưới 3 ký tự
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 422

    def test_register_username_too_long(self, client):
        """Test đăng ký với username quá dài."""
        register_data = {
            "username": "a" * 51,  # Trên 50 ký tự
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 422

    def test_register_password_too_short(self, client):
        """Test đăng ký với mật khẩu quá ngắn."""
        register_data = {
            "username": "newuser",
            "password": "12345",  # Dưới 6 ký tự
            "confirm_password": "12345"
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 422

    def test_register_password_too_long(self, client):
        """Test đăng ký với mật khẩu quá dài."""
        register_data = {
            "username": "newuser",
            "password": "a" * 51,  # Trên 50 ký tự
            "confirm_password": "a" * 51
        }
        
        response = client.post("/api/auth/register", json=register_data)
        
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """Test đăng ký thiếu fields."""
        # Thiếu username
        register_data = {
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        }
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 422
        
        # Thiếu password
        register_data = {
            "username": "newuser",
            "confirm_password": "newpassword123"
        }
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 422
        
        # Thiếu confirm_password
        register_data = {
            "username": "newuser",
            "password": "newpassword123"
        }
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 422 