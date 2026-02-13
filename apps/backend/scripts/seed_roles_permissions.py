from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.auth.models import User
from src.config import settings
from src.constants import UserRole, UserStatus
from src.models import BaseModel

db_url = settings.DATABASE_URL
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
BaseModel.metadata.create_all(bind=engine)

print("🌱 Bắt đầu tạo seed data cho roles và permissions...")

# Kiểm tra xem có user nào trong hệ thống không
user_count = session.query(User).count()
if user_count == 0:
    print("⚠️  Chưa có user nào trong hệ thống. Vui lòng chạy seed_users.py trước!")
    session.close()
    exit(1)

# Hiển thị thông tin về các user hiện có
print(f"📊 Tìm thấy {user_count} user(s) trong hệ thống:")
users = session.query(User).all()
for user in users:
    print(f"   - {user.username} ({user.role.value}) - {user.full_name}")

print("\n✅ Roles và permissions đã được thiết lập tự động thông qua UserRole enum")
print("   Các roles hiện có:")
for role in UserRole:
    print(f"   - {role.value}")

session.close()
print("\n🎉 Hoàn thành tạo seed data cho roles và permissions!")
