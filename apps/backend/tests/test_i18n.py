"""Unit tests cho i18n.py."""

import pytest
from unittest.mock import patch, Mock
from src.i18n import gettext, ngettext, i18n


class TestI18n:
    """Test cases cho internationalization."""

    def test_gettext_default(self):
        """Test gettext với locale mặc định."""
        # Test với message đơn giản
        result = gettext("Hello World")
        assert result == "Hello World"  # Fallback to original

    def test_gettext_with_locale(self):
        """Test gettext với locale cụ thể."""
        # Test với locale vi
        i18n.set_locale("vi")
        result = gettext("Hello World")
        assert result == "Hello World"  # Fallback to original khi không có translation

    def test_get_locale_default(self):
        """Test get_locale với giá trị mặc định."""
        locale = i18n._current_locale
        assert locale in ["vi", "en", "fr"]  # Default locale

    def test_get_locale_set(self):
        """Test get_locale với locale đã set."""
        i18n.set_locale("en")
        assert i18n._current_locale == "en"

    def test_set_locale(self):
        """Test set_locale function."""
        i18n.set_locale("fr")
        assert i18n._current_locale == "fr"

    def test_gettext_special_characters(self):
        """Test gettext với ký tự đặc biệt."""
        message = "Test message with @#$%^&*()"
        result = gettext(message)
        assert result == message

    def test_gettext_unicode(self):
        """Test gettext với unicode."""
        message = "Test message với tiếng Việt"
        result = gettext(message)
        assert result == message

    def test_gettext_empty_string(self):
        """Test gettext với string rỗng."""
        result = gettext("")
        assert result == ""

    def test_gettext_none(self):
        """Test gettext với None."""
        result = gettext(None)
        assert result is None

    def test_gettext_invalid_locale(self):
        """Test gettext với locale không hợp lệ."""
        i18n.set_locale("invalid_locale")
        result = gettext("Hello World")
        assert result == "Hello World"  # Fallback to original

    def test_locale_switching(self):
        """Test chuyển đổi locale."""
        i18n.set_locale("en")
        assert i18n._current_locale == "en"
        
        i18n.set_locale("vi")
        assert i18n._current_locale == "vi"
        
        i18n.set_locale("fr")
        assert i18n._current_locale == "fr"

    def test_ngettext_singular(self):
        """Test ngettext với số ít."""
        result = ngettext("1 item", "2 items", 1)
        assert result == "1 item"

    def test_ngettext_plural(self):
        """Test ngettext với số nhiều."""
        result = ngettext("1 item", "2 items", 2)
        assert result == "2 items"

    def test_ngettext_zero(self):
        """Test ngettext với số 0."""
        result = ngettext("1 item", "2 items", 0)
        assert result == "2 items"  # Zero uses plural form 