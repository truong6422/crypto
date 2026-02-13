"""Pytest configuration và fixtures cho testing."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, String, Column, Boolean, DateTime, Text, Integer, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from unittest.mock import Mock
import uuid

from src.main import app
from src.database import get_db
from src.auth.service import AuthService
from src.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Test Base for SQLite compatibility
TestBase = declarative_base()


class TestUser(TestBase):
    """Test User model with String IDs for SQLite compatibility."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    avatar_url = Column(String(500), nullable=True)

    # Audit fields
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    updated_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    deleted_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<TestUser(id={self.id}, username='{self.username}')>"


class TestAuthAuditLog(TestBase):
    """Test AuthAuditLog model with String IDs for SQLite compatibility."""
    __tablename__ = "auth_audit_log"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    action = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<TestAuthAuditLog(id={self.id}, action='{self.action}', success={self.success})>"


class TestFailedLoginAttempt(TestBase):
    """Test FailedLoginAttempt model with String IDs for SQLite compatibility."""
    __tablename__ = "failed_login_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    attempt_count = Column(Integer, default=1, nullable=False)
    first_attempt_at = Column(DateTime, default=func.now(), nullable=False)
    last_attempt_at = Column(DateTime, default=func.now(), nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    blocked_until = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TestFailedLoginAttempt(username='{self.username}', attempts={self.attempt_count}, blocked={self.is_blocked})>"


@pytest.fixture(scope="session")
def test_db():
    """Tạo test database."""
    TestBase.metadata.create_all(bind=engine)
    yield
    TestBase.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Tạo database session cho test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Tạo test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db_session):
    """Tạo sample user cho testing."""
    user = TestUser(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Tạo admin user cho testing."""
    user = TestUser(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        full_name="Admin User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(client, admin_user):
    """Tạo admin token cho testing."""
    login_data = {
        "username": "admin",
        "password": "adminpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    return response.json()["access_token"]


@pytest.fixture
def test_user(db_session):
    """Tạo test user cho testing."""
    user = TestUser(
        username="testuser2",
        email="test2@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User 2",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_service(db_session):
    """Tạo AuthService instance cho testing."""
    return AuthService(db_session)


@pytest.fixture
def mock_celery():
    """Mock Celery cho testing."""
    mock_celery = Mock()
    mock_celery.delay = Mock()
    return mock_celery