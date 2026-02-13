"""Unit tests cho Category model."""

import pytest
from sqlalchemy.orm import Session
from src.models import Category
from src.database import get_db
import uuid


class TestCategoryModel:
    """Test cases cho Category model."""
    
    def test_create_category(self, db_session: Session):
        """Test tạo category mới."""
        category = Category(
            name="Test Category",
            code=f"TEST_{uuid.uuid4().hex[:8]}",
            value="Test Value",
            description="Test Description",
            is_active=True,
            created_by="test_user"
        )
        
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.code.startswith("TEST_")
        assert category.value == "Test Value"
        assert category.description == "Test Description"
        assert category.is_active is True
        assert category.created_by == "test_user"
        assert category.is_deleted is False
    
    def test_create_category_with_parent(self, db_session: Session):
        """Test tạo category với parent."""
        # Tạo parent category
        parent = Category(
            name="Parent Category",
            code=f"PARENT_{uuid.uuid4().hex[:8]}",
            value="Parent Value",
            created_by="test_user"
        )
        db_session.add(parent)
        db_session.commit()
        db_session.refresh(parent)
        
        # Tạo child category
        child = Category(
            name="Child Category",
            code=f"CHILD_{uuid.uuid4().hex[:8]}",
            value="Child Value",
            parent_id=parent.id,
            created_by="test_user"
        )
        db_session.add(child)
        db_session.commit()
        db_session.refresh(child)
        
        assert child.parent_id == parent.id
        assert child.parent is not None
        assert child.parent.name == "Parent Category"
    
    def test_soft_delete_category(self, db_session: Session):
        """Test soft delete category."""
        category = Category(
            name="Test Category",
            code=f"TEST_{uuid.uuid4().hex[:8]}",
            value="Test Value",
            created_by="test_user"
        )
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        # Soft delete
        category.soft_delete("test_user", db_session)
        
        assert category.is_deleted is True
        assert category.deleted_by == "test_user"
        assert category.deleted_at is not None
    
    def test_get_active_records(self, db_session: Session):
        """Test lấy active records."""
        # Tạo active category
        active_category = Category(
            name="Active Category",
            code=f"ACTIVE_{uuid.uuid4().hex[:8]}",
            value="Active Value",
            created_by="test_user"
        )
        db_session.add(active_category)
        
        # Tạo deleted category
        deleted_category = Category(
            name="Deleted Category",
            code=f"DELETED_{uuid.uuid4().hex[:8]}",
            value="Deleted Value",
            created_by="test_user"
        )
        db_session.add(deleted_category)
        db_session.commit()
        
        # Soft delete one category
        deleted_category.soft_delete("test_user", db_session)
        
        # Lấy active records
        active_records = Category.get_active_records(db_session).all()
        
        # Kiểm tra xem có ít nhất 1 item active (bao gồm cả dữ liệu có sẵn)
        assert len(active_records) >= 1
        # Kiểm tra xem tất cả items đều không bị deleted
        for record in active_records:
            assert record.is_deleted is False
        # Kiểm tra xem active_category có trong danh sách
        found_active = False
        for record in active_records:
            if record.name == "Active Category" and record.code == active_category.code:
                found_active = True
                break
        assert found_active, "Không tìm thấy active category trong danh sách"
    
    def test_category_relationships(self, db_session: Session):
        """Test relationships giữa categories."""
        # Tạo parent
        parent = Category(
            name="Parent",
            code=f"PARENT_{uuid.uuid4().hex[:8]}",
            value="Parent Value",
            created_by="test_user"
        )
        db_session.add(parent)
        db_session.commit()
        db_session.refresh(parent)
        
        # Tạo children
        child1 = Category(
            name="Child 1",
            code=f"CHILD1_{uuid.uuid4().hex[:8]}",
            value="Child 1 Value",
            parent_id=parent.id,
            created_by="test_user"
        )
        child2 = Category(
            name="Child 2",
            code=f"CHILD2_{uuid.uuid4().hex[:8]}",
            value="Child 2 Value",
            parent_id=parent.id,
            created_by="test_user"
        )
        db_session.add_all([child1, child2])
        db_session.commit()
        db_session.refresh(parent)
        
        # Test parent-child relationships
        assert len(parent.children) == 2
        assert child1.parent_id == parent.id
        assert child2.parent_id == parent.id
        assert child1.parent.name == "Parent"
        assert child2.parent.name == "Parent"


@pytest.fixture
def db_session():
    """Fixture để tạo database session cho testing."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close() 