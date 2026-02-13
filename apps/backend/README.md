# HMS-PSY Backend API

Hệ thống quản lý hồ sơ chăm sóc sức khỏe người bệnh tâm thần - Backend API

## 🚀 Tính năng

- **Authentication & Authorization**: JWT-based authentication với role-based access control
- **User Management**: Quản lý người dùng, roles, permissions
- **API Documentation**: Tự động generate với FastAPI
- **Database**: PostgreSQL với SQLAlchemy ORM
- **Testing**: Unit tests và integration tests
- **Internationalization**: Hỗ trợ đa ngôn ngữ (vi, en, fr)

## 📋 API Endpoints

### Authentication
```
POST   /api/v1/auth/login              # Đăng nhập
GET    /api/v1/auth/me                 # Lấy thông tin user hiện tại
POST   /api/v1/auth/refresh            # Refresh token
POST   /api/v1/auth/logout             # Đăng xuất
POST   /api/v1/auth/change-password    # Đổi mật khẩu
POST   /api/v1/auth/forgot-password    # Quên mật khẩu
POST   /api/v1/auth/reset-password     # Reset mật khẩu
```

### User Management
```
GET    /api/v1/users                   # Danh sách users (có phân trang)
POST   /api/v1/users                   # Tạo user mới
GET    /api/v1/users/{user_id}         # Lấy thông tin user
PUT    /api/v1/users/{user_id}         # Cập nhật user
DELETE /api/v1/users/{user_id}         # Xóa user
PATCH  /api/v1/users/{user_id}/status  # Thay đổi trạng thái user
PUT    /api/v1/users/{user_id}/permissions  # Cập nhật permissions
POST   /api/v1/users/{user_id}/avatar  # Upload avatar
```

### Role Management
```
GET    /api/v1/roles                   # Danh sách roles
POST   /api/v1/roles                   # Tạo role mới
GET    /api/v1/roles/{role_id}         # Lấy thông tin role
PUT    /api/v1/roles/{role_id}         # Cập nhật role
DELETE /api/v1/roles/{role_id}         # Xóa role
```

### Permission Management
```
GET    /api/v1/permissions             # Danh sách permissions
POST   /api/v1/permissions             # Tạo permission mới
GET    /api/v1/permissions/{permission_id}  # Lấy thông tin permission
PUT    /api/v1/permissions/{permission_id}  # Cập nhật permission
DELETE /api/v1/permissions/{permission_id}  # Xóa permission
```

## 🔧 Cài đặt

### Yêu cầu hệ thống
- Python 3.9+
- PostgreSQL 12+
- Redis (cho Celery tasks)

### Cài đặt dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt  # Cho development
```

### Cấu hình môi trường
```bash
cp env.development.example env.development
# Chỉnh sửa các biến môi trường trong env.development
```

### Khởi tạo database
```bash
# Tạo database
python scripts/create_postgres_db.py

# Chạy migrations
alembic upgrade head

# Seed dữ liệu ban đầu
python scripts/seed_all.py
```

### Chạy ứng dụng
```bash
# Development
python run.py

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## 🧪 Testing

```bash
# Chạy tất cả tests
pytest

# Chạy tests với coverage
pytest --cov=src

# Chạy tests cụ thể
pytest tests/api/test_auth.py -v
```

## 📚 API Documentation

Sau khi chạy ứng dụng, truy cập:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔐 Authentication

API sử dụng JWT Bearer token:

```bash
# Login để lấy token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'

# Sử dụng token trong các request khác
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer <your_token>"
```

## 📊 Response Format

### Success Response
```json
{
  "data": {
    "id": "user_id",
    "username": "username",
    "email": "email@example.com",
    "role": "admin",
    "status": "active"
  },
  "status": 200
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": 400
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5,
  "has_next": true,
  "has_prev": false
}
```

## 🌐 Internationalization

Hệ thống hỗ trợ đa ngôn ngữ:
- **Vietnamese (vi)**: Mặc định
- **English (en)**: Hỗ trợ
- **French (fr)**: Hỗ trợ

Sử dụng header `Accept-Language` để chọn ngôn ngữ:
```bash
curl -H "Accept-Language: en" http://localhost:8000/api/v1/users
```

## 🔧 Development

### Code Style
- Sử dụng **flake8** với max line length 120
- **Black** cho code formatting
- **isort** cho import sorting

### Database Migrations
```bash
# Tạo migration mới
alembic revision --autogenerate -m "Description"

# Chạy migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Adding New Endpoints
1. Tạo model trong `src/models.py`
2. Tạo schema trong `src/schemas.py`
3. Tạo service trong `src/services/`
4. Tạo router trong `src/routers/`
5. Thêm router vào `src/main.py`
6. Viết tests trong `tests/`

## 📝 License

MIT License - xem file LICENSE để biết thêm chi tiết. 