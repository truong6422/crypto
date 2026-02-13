"""Unit tests cho core/security.py."""

import pytest
from src.core.security import get_password_hash, verify_password


class TestSecurity:
    """Test cases cho password hashing và verification."""

    def test_get_password_hash(self):
        """Test tạo password hash."""
        password = "testpassword123"
        hash_result = get_password_hash(password)
        
        assert hash_result is not None
        assert isinstance(hash_result, str)
        assert hash_result != password
        assert len(hash_result) > len(password)

    def test_verify_password_correct(self):
        """Test verify password đúng."""
        password = "testpassword123"
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_verify_password_incorrect(self):
        """Test verify password sai."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hash_result = get_password_hash(password)
        
        assert verify_password(wrong_password, hash_result) is False

    def test_verify_password_empty(self):
        """Test verify password rỗng."""
        password = ""
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_verify_password_special_chars(self):
        """Test verify password với ký tự đặc biệt."""
        password = "test@#$%^&*()_+{}|:<>?[]\\;'\",./"
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True

    def test_verify_password_unicode(self):
        """Test verify password với unicode."""
        password = "testpassword123中文"
        hash_result = get_password_hash(password)
        
        assert verify_password(password, hash_result) is True 