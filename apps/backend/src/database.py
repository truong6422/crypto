"""Cấu hình database và session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Optional

# Import models để đảm bảo chúng được tạo trong database
from .models import Base, User, AuthAuditLog, FailedLoginAttempt

# Lazy loading engine và session
_engine: Optional[object] = None
_SessionLocal: Optional[object] = None


def get_engine():
    """Lazy load engine."""
    global _engine
    if _engine is None:
        from .config import settings
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300
        )
    return _engine


def get_session_local():
    """Lazy load session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """
    Dependency để lấy database session.
    
    Yields:
        Session: Database session
    """
    db = get_session_local()()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=get_engine()) 