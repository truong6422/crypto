"""Unit tests cho database.py."""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.database import get_engine, get_session_local, Base, get_db


class TestDatabase:
    """Test cases cho database configuration."""

    def test_engine_creation(self):
        """Test engine được tạo thành công."""
        engine = get_engine()
        assert engine is not None
        assert str(engine.url).startswith("postgresql://")

    def test_session_local_creation(self):
        """Test SessionLocal được tạo thành công."""
        session_local = get_session_local()
        assert session_local is not None
        assert hasattr(session_local, '__call__')

    def test_base_creation(self):
        """Test Base được tạo thành công."""
        assert Base is not None
        # Base is a declarative base, not a table itself
        assert hasattr(Base, 'metadata')

    def test_get_db_generator(self):
        """Test get_db là generator function."""
        db_gen = get_db()
        assert hasattr(db_gen, '__iter__')
        assert hasattr(db_gen, '__next__')

    def test_get_db_session_type(self):
        """Test get_db trả về Session."""
        db_gen = get_db()
        db = next(db_gen)
        assert isinstance(db, Session)

    def test_get_db_session_cleanup(self):
        """Test get_db cleanup session."""
        with patch('src.database.get_session_local') as mock_get_session_local:
            mock_session_local = Mock()
            mock_session = Mock()
            mock_session_local.return_value = mock_session
            mock_get_session_local.return_value = mock_session_local
            
            db_gen = get_db()
            db = next(db_gen)
            
            # Simulate cleanup
            try:
                next(db_gen)
            except StopIteration:
                pass
            
            mock_session.close.assert_called_once()

    def test_base_inheritance(self):
        """Test Base có thể được kế thừa."""
        from sqlalchemy import Column, String
        
        class TestModel(Base):
            __tablename__ = "test_table"
            id = Column(String, primary_key=True)
        
        assert hasattr(TestModel, '__tablename__')
        assert TestModel.__tablename__ == "test_table"

    def test_session_local_configuration(self):
        """Test SessionLocal configuration."""
        session_local = get_session_local()
        # Test autocommit=False
        assert session_local.kw.get('autocommit') is False
        # Test autoflush=False
        assert session_local.kw.get('autoflush') is False

    def test_engine_configuration(self):
        """Test engine configuration."""
        engine = get_engine()
        # Test pool_pre_ping=True
        assert engine.pool._pre_ping is True
        # Test pool_recycle=300
        assert engine.pool._recycle == 300 