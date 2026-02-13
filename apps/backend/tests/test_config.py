"""Unit tests cho config.py."""

import pytest
from src.config import settings


class TestConfig:
    """Test cases cho configuration."""

    def test_default_settings(self):
        """Test các giá trị mặc định của settings."""
        assert settings.SECRET_KEY == "your-secret-key-here-change-in-production"
        assert settings.ALGORITHM == "HS256"
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert settings.APP_NAME == "Hệ Thống Quản Lý Bệnh Viện"
        assert settings.PROJECT_NAME == "HMS-PSY-INISOFT-2025"
        assert settings.API_V1_PREFIX == "/api/v1"
        assert settings.DEFAULT_PAGE_SIZE == 20
        assert settings.MAX_PAGE_SIZE == 100
        assert settings.DEFAULT_LOCALE == "vi"
        assert "vi" in settings.SUPPORTED_LOCALES
        assert "en" in settings.SUPPORTED_LOCALES
        assert "fr" in settings.SUPPORTED_LOCALES

    def test_database_urls(self):
        """Test database URLs."""
        assert "postgresql" in settings.DATABASE_URL
        assert "hms_psy_dev" in settings.DATABASE_URL
        assert settings.DATABASE_TEST_URL is not None
        assert "hms_psy_test" in settings.DATABASE_TEST_URL

    def test_celery_settings(self):
        """Test Celery settings."""
        assert "redis" in settings.CELERY_BROKER_URL
        assert "redis" in settings.CELERY_RESULT_BACKEND
        assert "redis" in settings.REDIS_URL

    def test_email_settings(self):
        """Test email settings."""
        assert settings.SMTP_HOST == "localhost"
        assert settings.SMTP_PORT == 587

    def test_cors_settings(self):
        """Test CORS settings."""
        assert "localhost:5173" in settings.CORS_ORIGINS
        assert "127.0.0.1:5173" in settings.CORS_ORIGINS

    def test_aws_settings(self):
        """Test AWS settings."""
        assert settings.AWS_REGION == "us-east-1"
        # AWS credentials có thể None trong development
        assert settings.AWS_ACCESS_KEY_ID is None or isinstance(settings.AWS_ACCESS_KEY_ID, str)
        assert settings.AWS_SECRET_ACCESS_KEY is None or isinstance(settings.AWS_SECRET_ACCESS_KEY, str)

    def test_environment_settings(self):
        """Test environment settings."""
        assert settings.ENVIRONMENT in ["development", "production", "testing"]
        assert isinstance(settings.DEBUG, bool)

    def test_pagination_settings(self):
        """Test pagination settings."""
        assert settings.DEFAULT_PAGE_SIZE > 0
        assert settings.MAX_PAGE_SIZE > settings.DEFAULT_PAGE_SIZE
        assert settings.MAX_PAGE_SIZE <= 1000  # Reasonable max

    def test_locale_settings(self):
        """Test locale settings."""
        assert len(settings.SUPPORTED_LOCALES) >= 1
        assert settings.DEFAULT_LOCALE in settings.SUPPORTED_LOCALES
        assert settings.LOCALE_PATH == "locales" 