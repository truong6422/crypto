"""Cấu hình toàn cục cho ứng dụng."""
import os
from pathlib import Path
from typing import Optional, ClassVar

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
# Find backend base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the backend directory
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Cài đặt ứng dụng được tải từ biến môi trường và file .env."""

    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/crypto_db"
    DATABASE_TEST_URL: Optional[str] = os.getenv(
        "DATABASE_TEST_URL", "postgresql://postgres:postgres@localhost:5432/crypto_test"
    )

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    REFRESH_TOKEN_EXPIRE_DAYS_REMEMBER: int = 30
    
    # Rate limiting
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 15

    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: Optional[str] = os.getenv("S3_BUCKET_NAME", None)

    # Application
    APP_NAME: str = "Crypto Base System"
    PROJECT_NAME: str = "Crypto-Base"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080"]')
    ALLOWED_ORIGINS: list = []

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Internationalization
    DEFAULT_LOCALE: str = "vi"
    SUPPORTED_LOCALES: list = ["vi", "en", "fr"]
    LOCALE_PATH: str = "locales"

    # File upload
    UPLOAD_DIR: str = "static/avatars"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        env_file = env_path
        case_sensitive = True
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Debug environment variables
        print("=== Environment Variables Debug ===")
        print(f"DATABASE_URL from env: {os.getenv('DATABASE_URL')}")
        print(f"REDIS_URL from env: {os.getenv('REDIS_URL')}")
        print(f"ENVIRONMENT from env: {os.getenv('ENVIRONMENT')}")
        print(f"DEBUG from env: {os.getenv('DEBUG')}")
        print("===================================")
        
        # Render specific configurations
        if os.getenv("DATABASE_URL"):
            # Render provides DATABASE_URL with postgres:// prefix
            # but SQLAlchemy expects postgresql://
            database_url = os.getenv("DATABASE_URL")
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql://", 1)
            self.DATABASE_URL = database_url
            print(f"Final DATABASE_URL: {self.DATABASE_URL}")
        
        if os.getenv("REDIS_URL"):
            self.REDIS_URL = os.getenv("REDIS_URL")
            print(f"Final REDIS_URL: {self.REDIS_URL}")
        
        # Parse CORS origins
        import json
        try:
            if isinstance(self.CORS_ORIGINS, str):
                self.ALLOWED_ORIGINS = json.loads(self.CORS_ORIGINS)
            else:
                self.ALLOWED_ORIGINS = self.CORS_ORIGINS
        except (json.JSONDecodeError, TypeError):
            # Fallback to default origins
            self.ALLOWED_ORIGINS = [
                "http://localhost:8080",
                "http://localhost:3000", 
                "http://localhost:5173"
            ]
            
        # Set production settings
        if self.ENVIRONMENT == "production":
            self.DEBUG = False
            print(f"Production mode - DEBUG: {self.DEBUG}")
            print(f"Production mode - ALLOWED_ORIGINS: {self.ALLOWED_ORIGINS}")
            
            # Ensure production frontend URL is in allowed origins
            production_frontend = "https://daily-home-meals-frontend.onrender.com"
            if production_frontend not in self.ALLOWED_ORIGINS:
                self.ALLOWED_ORIGINS.append(production_frontend)
                print(f"Added production frontend URL to allowed origins: {production_frontend}")


settings = Settings()
