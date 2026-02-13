"""Unit tests cho core/utils.py."""

import pytest
from datetime import datetime, timezone
from src.core.utils import generate_uuid, safe_get, format_error_message, validate_required_fields


class TestCoreUtils:
    """Test cases cho core utilities."""

    def test_generate_uuid(self):
        """Test tạo UUID."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        
        assert uuid1 is not None
        assert isinstance(uuid1, str)
        assert len(uuid1) > 0
        assert uuid1 != uuid2  # UUID phải unique

    def test_safe_get(self):
        """Test safe_get function."""
        test_dict = {"key1": "value1", "key2": "value2"}
        
        # Test existing key
        result = safe_get(test_dict, "key1")
        assert result == "value1"
        
        # Test non-existing key with default
        result = safe_get(test_dict, "key3", "default")
        assert result == "default"
        
        # Test non-existing key without default
        result = safe_get(test_dict, "key3")
        assert result is None

    def test_format_error_message(self):
        """Test format_error_message function."""
        # Test valid format
        result = format_error_message("Hello {name}", name="World")
        assert result == "Hello World"
        
        # Test invalid format
        result = format_error_message("Hello {name}")
        assert result == "Hello {name}"
        
        # Test with no parameters
        result = format_error_message("Simple message")
        assert result == "Simple message"

    def test_validate_required_fields(self):
        """Test validate_required_fields function."""
        test_data = {"field1": "value1", "field2": "value2", "field3": None}
        required_fields = ["field1", "field2", "field3", "field4"]
        
        missing_fields = validate_required_fields(test_data, required_fields)
        
        assert "field3" in missing_fields  # None value
        assert "field4" in missing_fields  # Missing field
        assert "field1" not in missing_fields  # Present
        assert "field2" not in missing_fields  # Present 