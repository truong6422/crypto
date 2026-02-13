"""Script tạo seed data cho users đơn giản."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.auth.models import User
from src.constants import UserStatus
from src.models import BaseModel
from src.core.security import get_password_hash

# Get DATABASE_URL directly from environment
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/daily_meals_dev")

# Fix postgres:// to postgresql:// for SQLAlchemy
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

print(f"Using database URL: {db_url}")

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
BaseModel.metadata.create_all(bind=engine)

print("🌱 Bắt đầu tạo seed data cho users...")

# Kiểm tra xem có user nào trong hệ thống không
user_count = session.query(User).count()
if user_count > 0:
    print(f"📊 Tìm thấy {user_count} user(s) trong hệ thống:")
    users = session.query(User).all()
    for user in users:
        print(f"   - {user.username} - {user.full_name} ({user.status.value})")
    session.close()
    print("\n✅ Users đã tồn tại, không cần tạo thêm!")
    exit(0)

# Tạo users mẫu
users_data = [
    {
        "username": "admin",
        "email": "admin@daily-meals.com",
        "full_name": "Administrator",
        "password": "admin123",
        "status": UserStatus.ACTIVE
    },
    {
        "username": "chef",
        "email": "chef@daily-meals.com", 
        "full_name": "Head Chef",
        "password": "chef123",
        "status": UserStatus.ACTIVE
    },
    {
        "username": "nutritionist",
        "email": "nutritionist@daily-meals.com",
        "full_name": "Nutrition Expert",
        "password": "nutri123", 
        "status": UserStatus.ACTIVE
    }
]

print("👥 Tạo users mẫu...")
for user_data in users_data:
    # Kiểm tra xem user đã tồn tại chưa
    existing_user = session.query(User).filter(User.username == user_data["username"]).first()
    if existing_user:
        print(f"   ⚠️  User {user_data['username']} đã tồn tại, bỏ qua")
        continue
    
    # Tạo user mới
    hashed_password = get_password_hash(user_data["password"])
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        full_name=user_data["full_name"],
        hashed_password=hashed_password,
        status=user_data["status"]
    )
    
    session.add(user)
    print(f"   ✅ Tạo user: {user_data['username']} - {user_data['full_name']}")

# Commit changes
session.commit()

# Hiển thị kết quả
print(f"\n📊 Tổng cộng có {session.query(User).count()} user(s) trong hệ thống:")
users = session.query(User).all()
for user in users:
    print(f"   - {user.username} - {user.full_name} ({user.status.value})")

session.close()
print("\n🎉 Hoàn thành tạo seed data cho users!")
print("\n📝 Demo Credentials:")
print("   admin / admin123")
print("   chef / chef123") 
print("   nutritionist / nutri123")
