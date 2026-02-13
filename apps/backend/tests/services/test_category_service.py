"""Unit tests cho Category service."""

import pytest
from sqlalchemy.orm import Session
from src.categories.service import CategoryService
from src.models import Category
from src.schemas import CategoryCreate, CategoryUpdate
from src.auth.exceptions import CategoryNotFoundError, CategoryAlreadyExistsError
import uuid


class TestCategoryService:
    """Test cases cho CategoryService."""
    
    def test_create_category_success(self, db_session: Session):
        """Test tạo category thành công."""
        service = CategoryService(db_session)
        
        category_data = CategoryCreate(
            name="Test Category",
            code=f"TEST_{uuid.uuid4().hex[:8]}",
            value="Test Value",
            description="Test Description",
            is_active=True
        )
        
        category = service.create_category(category_data, "test_user")
        
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.code == category_data.code
        assert category.value == "Test Value"
        assert category.created_by == "test_user"
    
    def test_create_category_duplicate_code(self, db_session: Session):
        """Test tạo category với code đã tồn tại."""
        service = CategoryService(db_session)
        
        # Tạo category đầu tiên
        unique_code = f"TEST_{uuid.uuid4().hex[:8]}"
        category_data1 = CategoryCreate(
            name="Test Category 1",
            code=unique_code,
            value="Test Value 1",
            is_active=True
        )
        service.create_category(category_data1, "test_user")
        
        # Tạo category thứ hai với cùng code
        category_data2 = CategoryCreate(
            name="Test Category 2",
            code=unique_code,
            value="Test Value 2",
            is_active=True
        )
        
        with pytest.raises(CategoryAlreadyExistsError):
            service.create_category(category_data2, "test_user")
    
    def test_create_category_with_invalid_parent(self, db_session: Session):
        """Test tạo category với parent_id không tồn tại."""
        service = CategoryService(db_session)
        
        category_data = CategoryCreate(
            name="Test Category",
            code=f"TEST_{uuid.uuid4().hex[:8]}",
            value="Test Value",
            parent_id="non-existent-id",
            is_active=True
        )
        
        with pytest.raises(CategoryNotFoundError):
            service.create_category(category_data, "test_user")
    
    def test_get_category_by_id_success(self, db_session: Session):
        """Test lấy category theo ID thành công."""
        service = CategoryService(db_session)
        
        # Tạo category
        category_data = CategoryCreate(
            name="Test Category",
            code=f"TEST_{uuid.uuid4().hex[:8]}",
            value="Test Value",
            is_active=True
        )
        created_category = service.create_category(category_data, "test_user")
        
        # Lấy category theo ID
        category = service.get_category_by_id(created_category.id)
        
        assert category is not None
        assert category.name == "Test Category"
        assert category.code == category_data.code
    
    def test_get_category_by_id_not_found(self, db_session: Session):
        """Test lấy category theo ID không tồn tại."""
        service = CategoryService(db_session)
        
        category = service.get_category_by_id("non-existent-id")
        
        assert category is None
    
    def test_get_category_by_code_success(self, db_session: Session):
        """Test lấy category theo code thành công."""
        service = CategoryService(db_session)
        
        # Tạo category
        unique_code = f"TEST_{uuid.uuid4().hex[:8]}"
        category_data = CategoryCreate(
            name="Test Category",
            code=unique_code,
            value="Test Value",
            is_active=True
        )
        service.create_category(category_data, "test_user")
        
        # Lấy category theo code
        category = service.get_category_by_code(unique_code)
        
        assert category is not None
        assert category.name == "Test Category"
        assert category.code == unique_code
    
    def test_get_categories_with_filters(self, db_session: Session):
        """Test lấy danh sách categories với filters."""
        service = CategoryService(db_session)
        
        # Tạo các categories
        categories_data = [
            CategoryCreate(name="Active Category", code=f"ACTIVE_{uuid.uuid4().hex[:8]}", value="Active", is_active=True),
            CategoryCreate(name="Inactive Category", code=f"INACTIVE_{uuid.uuid4().hex[:8]}", value="Inactive", is_active=False),
            CategoryCreate(name="Search Category", code=f"SEARCH_{uuid.uuid4().hex[:8]}", value="Search", is_active=True),
        ]
        
        for data in categories_data:
            service.create_category(data, "test_user")
        
        # Test filter theo is_active
        active_categories, total = service.get_categories(is_active=True)
        # Kiểm tra xem có ít nhất 2 items active (bao gồm cả dữ liệu có sẵn)
        assert len(active_categories) >= 2
        # Kiểm tra xem tất cả items đều active
        for category in active_categories:
            assert category.is_active is True
        
        # Test search
        search_categories, total = service.get_categories(search="Search")
        # Kiểm tra xem có ít nhất 1 item chứa "Search"
        assert len(search_categories) >= 1
        # Kiểm tra xem có item nào chứa "Search" trong tên
        found_search = False
        for category in search_categories:
            if "Search" in category.name:
                found_search = True
                break
        assert found_search, "Không tìm thấy category có tên chứa 'Search'"
    
    def test_update_category_success(self, db_session: Session):
        """Test cập nhật category thành công."""
        service = CategoryService(db_session)
        
        # Tạo category
        category_data = CategoryCreate(
            name="Original Name",
            code=f"ORIGINAL_{uuid.uuid4().hex[:8]}",
            value="Original Value",
            is_active=True
        )
        category = service.create_category(category_data, "test_user")
        
        # Cập nhật category
        update_data = CategoryUpdate(
            name="Updated Name",
            value="Updated Value"
        )
        updated_category = service.update_category(category.id, update_data, "test_user")
        
        assert updated_category.name == "Updated Name"
        assert updated_category.value == "Updated Value"
        assert updated_category.updated_by == "test_user"
    
    def test_update_category_not_found(self, db_session: Session):
        """Test cập nhật category không tồn tại."""
        service = CategoryService(db_session)
        
        update_data = CategoryUpdate(name="Updated Name")
        
        with pytest.raises(CategoryNotFoundError):
            service.update_category("non-existent-id", update_data, "test_user")
    
    def test_update_category_duplicate_code(self, db_session: Session):
        """Test cập nhật category với code đã tồn tại."""
        service = CategoryService(db_session)
        
        # Tạo 2 categories
        category1_data = CategoryCreate(name="Category 1", code=f"CODE1_{uuid.uuid4().hex[:8]}", value="Value 1", is_active=True)
        category2_data = CategoryCreate(name="Category 2", code=f"CODE2_{uuid.uuid4().hex[:8]}", value="Value 2", is_active=True)
        
        category1 = service.create_category(category1_data, "test_user")
        category2 = service.create_category(category2_data, "test_user")
        
        # Cập nhật category2 với code của category1
        update_data = CategoryUpdate(code=category1.code)
        
        with pytest.raises(CategoryAlreadyExistsError):
            service.update_category(category2.id, update_data, "test_user")
    
    def test_delete_category_success(self, db_session: Session):
        """Test xóa category thành công."""
        service = CategoryService(db_session)
        
        # Tạo category
        category_data = CategoryCreate(
            name="Test Category",
            code=f"TEST_{uuid.uuid4().hex[:8]}",
            value="Test Value",
            is_active=True
        )
        category = service.create_category(category_data, "test_user")
        
        # Xóa category
        result = service.delete_category(category.id, "test_user")
        
        assert result is True
        
        # Kiểm tra category đã bị soft delete
        deleted_category = service.get_category_by_id(category.id)
        assert deleted_category is None
    
    def test_delete_category_with_children(self, db_session: Session):
        """Test xóa category có children."""
        service = CategoryService(db_session)
        
        # Tạo parent category
        parent_data = CategoryCreate(name="Parent", code=f"PARENT_{uuid.uuid4().hex[:8]}", value="Parent", is_active=True)
        parent = service.create_category(parent_data, "test_user")
        
        # Tạo child category
        child_data = CategoryCreate(name="Child", code=f"CHILD_{uuid.uuid4().hex[:8]}", value="Child", parent_id=parent.id, is_active=True)
        service.create_category(child_data, "test_user")
        
        # Thử xóa parent category
        with pytest.raises(ValueError, match="Không thể xóa category có"):
            service.delete_category(parent.id, "test_user")
    
    def test_get_category_tree(self, db_session: Session):
        """Test lấy category tree."""
        service = CategoryService(db_session)
        
        # Tạo parent category
        parent_data = CategoryCreate(name="Parent", code=f"PARENT_{uuid.uuid4().hex[:8]}", value="Parent", is_active=True)
        parent = service.create_category(parent_data, "test_user")
        
        # Tạo child categories
        child1_data = CategoryCreate(name="Child 1", code=f"CHILD1_{uuid.uuid4().hex[:8]}", value="Child 1", parent_id=parent.id, is_active=True)
        child2_data = CategoryCreate(name="Child 2", code=f"CHILD2_{uuid.uuid4().hex[:8]}", value="Child 2", parent_id=parent.id, is_active=True)
        
        service.create_category(child1_data, "test_user")
        service.create_category(child2_data, "test_user")
        
        # Lấy category tree
        tree = service.get_category_tree()
        
        # Kiểm tra xem có ít nhất 1 item (parent category)
        assert len(tree) >= 1
        # Tìm parent category trong tree
        parent_found = False
        for item in tree:
            if item["name"] == "Parent" and item["code"] == parent.code:
                parent_found = True
                # Kiểm tra xem có 2 children
                assert len(item["children"]) == 2
                break
        assert parent_found, "Không tìm thấy parent category trong tree"


@pytest.fixture
def db_session():
    """Fixture để tạo database session cho testing."""
    from src.database import get_db
    db = next(get_db())
    try:
        yield db
    finally:
        db.close() 