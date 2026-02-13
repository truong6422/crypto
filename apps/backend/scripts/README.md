# Scripts Directory

Thư mục này chứa các script để quản lý database và tạo dữ liệu demo cho hệ thống.

## Các Script Có Sẵn

### 1. `reset_dev_db.py`
Reset database development PostgreSQL.

```bash
python scripts/reset_dev_db.py
```

**Yêu cầu:**
- PostgreSQL đang chạy
- Cấu hình database trong `env.development`

### 2. `seed_users.py`
Tạo các tài khoản demo với thông tin đăng nhập đơn giản.

```bash
python scripts/seed_users.py
```

**Tài khoản demo được tạo:**
- **Bác sĩ**: `doctor` / `123456`
- **Y tá**: `nurse` / `123456`
- **Quản trị**: `admin` / `123456`
- **Nhân viên**: `staff` / `123456`

### 3. `seed_permissions.py`
Thiết lập permissions và gán cho roles.

```bash
python scripts/seed_permissions.py
```

### 4. `seed_all.py` ⭐ (Khuyến nghị)
Script tổng hợp chạy migration và tất cả các script seed theo thứ tự đúng.

```bash
python scripts/seed_all.py
```

### 5. `fresh_start.py` 🆕 (Fresh Start)
Script để reset hoàn toàn database và chạy lại seed data.

```bash
python scripts/fresh_start.py
```

## Quy Trình Sử Dụng

### Lần đầu setup
```bash
# 1. Fresh start (khuyến nghị)
python scripts/fresh_start.py

# Hoặc từng bước:
# 1. Reset database
python scripts/reset_dev_db.py

# 2. Chạy migration và seed data
python scripts/seed_all.py
```

### Reset dữ liệu demo
```bash
# Cách 1: Fresh start (khuyến nghị)
python scripts/fresh_start.py

# Cách 2: Từng bước
python scripts/reset_dev_db.py
python scripts/seed_all.py
```

## Cấu Hình Database

### PostgreSQL (Bắt buộc)
```bash
# Trong env.development
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=hms_psy_dev
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hms_psy_dev
DATABASE_TEST_URL=postgresql://postgres:postgres@localhost:5432/hms_psy_test
```

## Lưu Ý

- Hệ thống chỉ hỗ trợ PostgreSQL
- Các tài khoản demo chỉ dành cho môi trường development
- Không sử dụng mật khẩu `123456` trong production
- Script `seed_all.py` sẽ tự động chạy migration trước khi seed
- Script `fresh_start.py` là cách nhanh nhất để reset hoàn toàn database
- Nếu user đã tồn tại, script sẽ bỏ qua và không tạo lại

## Troubleshooting

### Lỗi "Module not found"
Đảm bảo bạn đang chạy script từ thư mục `apps/backend`:
```bash
cd apps/backend
python scripts/fresh_start.py
```

### Lỗi database connection
Kiểm tra file `env.development` và đảm bảo `DATABASE_URL` được cấu hình đúng.

### Lỗi permission
Đảm bảo script có quyền thực thi:
```bash
chmod +x scripts/fresh_start.py
```

### Lỗi PostgreSQL
Đảm bảo PostgreSQL đang chạy và có thể kết nối được:
```bash
# Kiểm tra PostgreSQL service
sudo systemctl status postgresql

# Hoặc trên macOS
brew services list | grep postgresql

# Khởi động PostgreSQL nếu chưa chạy
sudo systemctl start postgresql
# Hoặc trên macOS
brew services start postgresql
``` 