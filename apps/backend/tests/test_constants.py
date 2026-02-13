"""Unit tests cho constants.py."""

import pytest
from src.constants import UserRole, UserStatus, Gender, AuditEventType, Messages, Config


class TestConstants:
    """Test cases cho constants."""

    def test_user_role_values(self):
        """Test UserRole enum values."""
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.DOCTOR.value == "doctor"
        assert UserRole.NURSE.value == "nurse"
        assert UserRole.STAFF.value == "staff"

    def test_user_role_membership(self):
        """Test UserRole enum membership."""
        assert UserRole.ADMIN in UserRole
        assert UserRole.DOCTOR in UserRole
        assert UserRole.NURSE in UserRole
        assert UserRole.STAFF in UserRole

    def test_user_status_values(self):
        """Test UserStatus enum values."""
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.INACTIVE.value == "inactive"
        assert UserStatus.SUSPENDED.value == "suspended"

    def test_user_status_membership(self):
        """Test UserStatus enum membership."""
        assert UserStatus.ACTIVE in UserStatus
        assert UserStatus.INACTIVE in UserStatus
        assert UserStatus.SUSPENDED in UserStatus

    def test_audit_event_type_values(self):
        """Test AuditEventType enum values."""
        assert AuditEventType.CREATE.value == "create"
        assert AuditEventType.UPDATE.value == "update"
        assert AuditEventType.DELETE.value == "delete"
        assert AuditEventType.LOGIN.value == "login"
        assert AuditEventType.LOGOUT.value == "logout"

    def test_audit_event_type_membership(self):
        """Test AuditEventType enum membership."""
        assert AuditEventType.CREATE in AuditEventType
        assert AuditEventType.UPDATE in AuditEventType
        assert AuditEventType.DELETE in AuditEventType
        assert AuditEventType.LOGIN in AuditEventType
        assert AuditEventType.LOGOUT in AuditEventType

    def test_gender_values(self):
        """Test Gender enum values."""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.OTHER.value == "other"

    def test_gender_membership(self):
        """Test Gender enum membership."""
        assert Gender.MALE in Gender
        assert Gender.FEMALE in Gender
        assert Gender.OTHER in Gender

    def test_user_role_validation(self):
        """Test UserRole validation."""
        # Test valid roles
        assert UserRole.ADMIN.value in [role.value for role in UserRole]
        assert UserRole.DOCTOR.value in [role.value for role in UserRole]
        
        # Test invalid role
        assert "INVALID_ROLE" not in [role.value for role in UserRole]

    def test_user_status_validation(self):
        """Test UserStatus validation."""
        # Test valid statuses
        assert UserStatus.ACTIVE.value in [status.value for status in UserStatus]
        assert UserStatus.INACTIVE.value in [status.value for status in UserStatus]
        
        # Test invalid status
        assert "INVALID_STATUS" not in [status.value for status in UserStatus]

    def test_audit_event_type_validation(self):
        """Test AuditEventType validation."""
        # Test valid event types
        assert AuditEventType.CREATE.value in [event.value for event in AuditEventType]
        assert AuditEventType.UPDATE.value in [event.value for event in AuditEventType]
        
        # Test invalid event type
        assert "invalid_event" not in [event.value for event in AuditEventType]

    def test_messages_constants(self):
        """Test Messages constants."""
        assert hasattr(Messages, 'AUTH_INVALID_CREDENTIALS')
        assert hasattr(Messages, 'USER_CREATED_SUCCESS')
        assert hasattr(Messages, 'ROLE_CREATED_SUCCESS')
        assert hasattr(Messages, 'VALIDATION_REQUIRED_FIELD')
        assert hasattr(Messages, 'SYSTEM_ERROR')

    def test_config_constants(self):
        """Test Config constants."""
        assert Config.DEFAULT_PAGE_SIZE == 20
        assert Config.MAX_PAGE_SIZE == 100
        assert Config.MIN_PASSWORD_LENGTH == 8
        assert Config.MAX_LOGIN_ATTEMPTS == 5
        assert Config.LOCKOUT_DURATION_MINUTES == 30
        assert Config.MAX_FILE_SIZE == 10 * 1024 * 1024
        assert Config.API_VERSION == "v1"
        assert Config.DEFAULT_LOCALE == "vi"
        assert "vi" in Config.SUPPORTED_LOCALES

    def test_allowed_file_types(self):
        """Test allowed file types."""
        assert "image/jpeg" in Config.ALLOWED_IMAGE_TYPES
        assert "image/png" in Config.ALLOWED_IMAGE_TYPES
        assert "application/pdf" in Config.ALLOWED_DOCUMENT_TYPES
        assert "application/msword" in Config.ALLOWED_DOCUMENT_TYPES

    def test_cache_constants(self):
        """Test cache constants."""
        assert Config.CACHE_TTL == 3600
        assert Config.CACHE_PREFIX == "hospital_management"

    def test_api_constants(self):
        """Test API constants."""
        assert Config.API_PREFIX == "/api/v1"
        assert Config.API_VERSION == "v1" 