"""API tests cho Category endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from src.main import app
from src.models import Category
from src.auth.models import User, Role
from src.database import get_db
from src.auth.dependencies import get_current_user
from src.constants import UserRole, UserStatus
import uuid

client = TestClient(app)


class TestCategoryAPI:
    """Test cases cho Category API endpoints."""
    
    def test_get_categories_unauthorized(self):
        """Test lấy danh sách categories không có authentication."""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 403  # Thay đổi từ 401 thành 403 vì endpoint yêu cầu admin
    
    def test_get_categories_public(self, db_session: Session):
        """Test lấy danh sách categories qua public endpoint (không cần authentication)."""
        # Tạo test categories với code unique
        categories = [
            Category(name="Public Test 1", code=f"PUBLIC1_{uuid.uuid4().hex[:8]}", value="Value 1", created_by="test_user"),
            Category(name="Public Test 2", code=f"PUBLIC2_{uuid.uuid4().hex[:8]}", value="Value 2", created_by="test_user"),
        ]
        for category in categories:
            db_session.add(category)
        db_session.commit()
        
        response = client.get("/api/v1/categories/public/")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 2
    
    def test_get_categories_authorized(self, db_session: Session, auth_headers):
        """Test lấy danh sách categories có authentication."""
        # Tạo test categories với code unique
        categories = [
            Category(name="Test 1", code=f"TEST1_{uuid.uuid4().hex[:8]}", value="Value 1", created_by="test_user"),
            Category(name="Test 2", code=f"TEST2_{uuid.uuid4().hex[:8]}", value="Value 2", created_by="test_user"),
        ]
        for category in categories:
            db_session.add(category)
        db_session.commit()
        
        response = client.get("/api/v1/categories/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 2
    
    def test_get_categories_with_filters(self, db_session: Session, auth_headers):
        """Test lấy danh sách categories với filters."""
        # Tạo test categories với code unique
        categories = [
            Category(name="Active Category", code=f"ACTIVE_{uuid.uuid4().hex[:8]}", value="Active", is_active=True, created_by="test_user"),
            Category(name="Inactive Category", code=f"INACTIVE_{uuid.uuid4().hex[:8]}", value="Inactive", is_active=False, created_by="test_user"),
        ]
        for category in categories:
            db_session.add(category)
        db_session.commit()
        
        # Test filter theo is_active
        response = client.get("/api/v1/categories/?is_active=true", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Kiểm tra xem có ít nhất 1 item active
        assert len(data["items"]) >= 1
        # Kiểm tra xem tất cả items đều active
        for item in data["items"]:
            assert item["is_active"] is True
        
        # Test search
        response = client.get("/api/v1/categories/?search=Active", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Kiểm tra xem có ít nhất 1 item chứa "Active"
        assert len(data["items"]) >= 1
        # Kiểm tra xem có item nào chứa "Active" trong tên
        found_active = False
        for item in data["items"]:
            if "Active" in item["name"]:
                found_active = True
                break
        assert found_active, "Không tìm thấy item có tên chứa 'Active'"
    
    def test_get_category_by_id_success(self, db_session: Session, auth_headers):
        """Test lấy category theo ID thành công."""
        # Tạo test category với code unique
        category = Category(name="Test Category", code=f"TEST_{uuid.uuid4().hex[:8]}", value="Test Value", created_by="test_user")
        db_session.add(category)
        db_session.commit()
        
        response = client.get(f"/api/v1/categories/{category.id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Category"
        assert data["code"] == category.code
    
    def test_get_category_by_id_not_found(self, auth_headers):
        """Test lấy category theo ID không tồn tại."""
        response = client.get("/api/v1/categories/non-existent-id", headers=auth_headers)
        assert response.status_code == 404
    
    def test_get_category_by_code_success(self, db_session: Session, auth_headers):
        """Test lấy category theo code thành công."""
        # Tạo test category với code unique
        unique_code = f"TEST_{uuid.uuid4().hex[:8]}"
        category = Category(name="Test Category", code=unique_code, value="Test Value", created_by="test_user")
        db_session.add(category)
        db_session.commit()
        
        response = client.get(f"/api/v1/categories/by-code/{unique_code}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Category"
        assert data["code"] == unique_code
    
    def test_get_category_by_code_not_found(self, auth_headers):
        """Test lấy category theo code không tồn tại."""
        response = client.get("/api/v1/categories/by-code/NONEXISTENT", headers=auth_headers)
        assert response.status_code == 404
    
    def test_create_category_unauthorized(self):
        """Test tạo category không có quyền admin."""
        category_data = {
            "name": "Test Category",
            "code": f"TEST_{uuid.uuid4().hex[:8]}",
            "value": "Test Value",
            "is_active": True
        }
        
        response = client.post("/api/v1/categories/", json=category_data)
        assert response.status_code == 403  # Endpoint yêu cầu admin role
    
    def test_create_category_authorized(self, db_session: Session, admin_headers):
        """Test tạo category có quyền admin."""
        category_data = {
            "name": "Test Category",
            "code": f"TEST_{uuid.uuid4().hex[:8]}",
            "value": "Test Value",
            "description": "Test Description",
            "is_active": True
        }
        
        response = client.post("/api/v1/categories/", json=category_data, headers=admin_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Test Category"
        assert data["code"] == category_data["code"]
        assert data["value"] == "Test Value"
        assert data["description"] == "Test Description"
    
    def test_create_category_duplicate_code(self, db_session: Session, admin_headers):
        """Test tạo category với code đã tồn tại."""
        # Tạo category đầu tiên
        unique_code = f"TEST_{uuid.uuid4().hex[:8]}"
        category1 = Category(name="Test 1", code=unique_code, value="Value 1", created_by="test_user")
        db_session.add(category1)
        db_session.commit()
        
        # Tạo category thứ hai với cùng code
        category_data = {
            "name": "Test 2",
            "code": unique_code,
            "value": "Value 2",
            "is_active": True
        }
        
        response = client.post("/api/v1/categories/", json=category_data, headers=admin_headers)
        assert response.status_code == 400
    
    def test_update_category_unauthorized(self, db_session: Session, auth_headers):
        """Test cập nhật category không có quyền admin."""
        # Tạo test category với code unique
        category = Category(name="Test Category", code=f"TEST_{uuid.uuid4().hex[:8]}", value="Test Value", created_by="test_user")
        db_session.add(category)
        db_session.commit()
        
        update_data = {"name": "Updated Name"}
        
        response = client.put(f"/api/v1/categories/{category.id}", json=update_data, headers=auth_headers)
        assert response.status_code == 403
    
    def test_update_category_authorized(self, db_session: Session, admin_headers):
        """Test cập nhật category có quyền admin."""
        # Tạo test category với code unique
        category = Category(name="Original Name", code=f"ORIGINAL_{uuid.uuid4().hex[:8]}", value="Original Value", created_by="test_user")
        db_session.add(category)
        db_session.commit()
        
        update_data = {
            "name": "Updated Name",
            "value": "Updated Value"
        }
        
        response = client.put(f"/api/v1/categories/{category.id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["value"] == "Updated Value"
    
    def test_update_category_not_found(self, admin_headers):
        """Test cập nhật category không tồn tại."""
        update_data = {"name": "Updated Name"}
        
        response = client.put("/api/v1/categories/non-existent-id", json=update_data, headers=admin_headers)
        assert response.status_code == 404
    
    def test_delete_category_unauthorized(self, db_session: Session, auth_headers):
        """Test xóa category không có quyền admin."""
        # Tạo test category với code unique
        category = Category(name="Test Category", code=f"TEST_{uuid.uuid4().hex[:8]}", value="Test Value", created_by="test_user")
        db_session.add(category)
        db_session.commit()
        
        response = client.delete(f"/api/v1/categories/{category.id}", headers=auth_headers)
        assert response.status_code == 403
    
    def test_delete_category_authorized(self, db_session: Session, admin_headers):
        """Test xóa category có quyền admin."""
        # Tạo test category với code unique
        category = Category(name="Test Category", code=f"TEST_{uuid.uuid4().hex[:8]}", value="Test Value", created_by="test_user")
        db_session.add(category)
        db_session.commit()
        
        response = client.delete(f"/api/v1/categories/{category.id}", headers=admin_headers)
        assert response.status_code == 204
    
    def test_delete_category_not_found(self, admin_headers):
        """Test xóa category không tồn tại."""
        response = client.delete("/api/v1/categories/non-existent-id", headers=admin_headers)
        assert response.status_code == 404
    
    def test_get_category_tree(self, db_session: Session, auth_headers):
        """Test lấy category tree."""
        # Tạo parent category với code unique
        parent = Category(name="Parent", code=f"PARENT_{uuid.uuid4().hex[:8]}", value="Parent", is_active=True, created_by="test_user")
        db_session.add(parent)
        db_session.commit()
        
        # Tạo child categories với code unique
        child1 = Category(name="Child 1", code=f"CHILD1_{uuid.uuid4().hex[:8]}", value="Child 1", parent_id=parent.id, is_active=True, created_by="test_user")
        child2 = Category(name="Child 2", code=f"CHILD2_{uuid.uuid4().hex[:8]}", value="Child 2", parent_id=parent.id, is_active=True, created_by="test_user")
        db_session.add_all([child1, child2])
        db_session.commit()
        
        response = client.get("/api/v1/categories/tree/list", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        # Kiểm tra xem có ít nhất 1 item (parent category)
        assert len(data) >= 1
        # Tìm parent category trong tree
        parent_found = False
        for item in data:
            if item["name"] == "Parent" and item["code"] == parent.code:
                parent_found = True
                # Kiểm tra xem có 2 children
                assert len(item["children"]) == 2
                break
        assert parent_found, "Không tìm thấy parent category trong tree"


@pytest.fixture
def db_session():
    """Fixture để tạo database session cho testing."""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_headers(db_session: Session):
    """Fixture để tạo authentication headers."""
    # Kiểm tra xem role "user" đã tồn tại chưa
    existing_role = db_session.query(Role).filter(Role.name == "user").first()
    if existing_role:
        role = existing_role
    else:
        # Tạo test user và role
        role = Role(name="user", description="Test user role")
        db_session.add(role)
        db_session.commit()
    
    # Kiểm tra xem user đã tồn tại chưa
    existing_user = db_session.query(User).filter(User.username == "testuser").first()
    if existing_user:
        user = existing_user
    else:
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role_id=role.id,
            status=UserStatus.ACTIVE
        )
        db_session.add(user)
        db_session.commit()
    
    # Mock authentication với session context
    def mock_get_current_user():
        # Đảm bảo user được load trong session hiện tại
        return db_session.merge(user)
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
def admin_headers(db_session: Session):
    """Fixture để tạo admin authentication headers."""
    # Kiểm tra xem role "admin" đã tồn tại chưa
    existing_role = db_session.query(Role).filter(Role.name == "admin").first()
    if existing_role:
        admin_role = existing_role
    else:
        # Tạo admin role
        admin_role = Role(name="admin", description="Admin role")
        db_session.add(admin_role)
        db_session.commit()
    
    # Kiểm tra xem admin user đã tồn tại chưa
    existing_user = db_session.query(User).filter(User.username == "admin").first()
    if existing_user:
        admin_user = existing_user
    else:
        # Tạo admin user
        admin_user = User(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password="hashed_password",
            role_id=admin_role.id,
            status=UserStatus.ACTIVE
        )
        db_session.add(admin_user)
        db_session.commit()
    
    # Mock authentication với session context
    def mock_get_current_user():
        # Đảm bảo user được load trong session hiện tại
        return db_session.merge(admin_user)
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    return {"Authorization": "Bearer admin_token"} 