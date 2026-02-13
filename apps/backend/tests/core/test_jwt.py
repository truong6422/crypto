"""Unit tests cho core/jwt.py."""

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from src.core.jwt import create_access_token, verify_token
from src.config import settings


class TestJWT:
    """Test cases cho JWT utilities."""

    def test_create_access_token(self):
        """Test tạo access token."""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"
        assert "exp" in payload

    def test_create_access_token_with_expires_delta(self):
        """Test tạo access token với expires_delta."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta)
        
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        
        # Check expiration
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Token should expire in about 60 minutes
        assert exp_datetime > now
        assert exp_datetime < now + timedelta(minutes=61)

    def test_verify_token_valid(self):
        """Test verify token hợp lệ."""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"

    def test_verify_token_invalid(self):
        """Test verify token không hợp lệ."""
        with pytest.raises(JWTError):
            verify_token("invalid_token")

    def test_verify_token_expired(self):
        """Test verify token đã hết hạn."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Expired 1 second ago
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(JWTError):
            verify_token(token)

    def test_create_access_token_empty_data(self):
        """Test tạo access token với data rỗng."""
        data = {}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload == {"exp": payload["exp"]}

    def test_create_access_token_none_data(self):
        """Test tạo access token với data None."""
        with pytest.raises(AttributeError):
            create_access_token(None)

    def test_token_algorithm(self):
        """Test token sử dụng đúng algorithm."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Decode without verification to check algorithm
        header = jwt.get_unverified_header(token)
        assert header["alg"] == settings.ALGORITHM

    def test_token_expiration_default(self):
        """Test token có expiration time mặc định."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert "exp" in payload
        
        # Check default expiration
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        default_expiry = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Allow small time difference (increased tolerance for timezone issues)
        assert abs((exp_datetime - default_expiry).total_seconds()) < 60

    def test_token_with_complex_data(self):
        """Test token với data phức tạp."""
        data = {
            "sub": "testuser",
            "user_id": "123",
            "roles": ["admin", "user"],
            "permissions": ["read", "write"],
            "metadata": {"department": "IT", "location": "HQ"}
        }
        token = create_access_token(data)
        
        payload = verify_token(token)
        assert payload["sub"] == "testuser"
        assert payload["user_id"] == "123"
        assert payload["roles"] == ["admin", "user"]
        assert payload["permissions"] == ["read", "write"]
        assert payload["metadata"]["department"] == "IT"
        assert payload["metadata"]["location"] == "HQ" 