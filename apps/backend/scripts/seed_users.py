#!/usr/bin/env python3
"""
Script để tạo seed data cho users.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.auth.models import User, Role
from src.config import settings
from src.constants import UserStatus
from src.core.security import get_password_hash
from src.models import BaseModel

db_url = settings.DATABASE_URL
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
BaseModel.metadata.create_all(bind=engine)


def create_roles():
    """Tạo các roles cần thiết."""
    roles_data = [
        {"name": "admin", "description": "Quản trị viên hệ thống"},
        {"name": "doctor", "description": "Bác sĩ"},
        {"name": "nurse", "description": "Y tá"},
        {"name": "staff", "description": "Nhân viên hành chính"},
    ]

    roles = {}
    for role_data in roles_data:
        existing_role = session.query(Role).filter_by(name=role_data["name"]).first()
        if existing_role:
            roles[role_data["name"]] = existing_role
            print(f"⚠️  Role {role_data['name']} đã tồn tại")
        else:
            new_role = Role(
                name=role_data["name"],
                description=role_data["description"]
            )
            session.add(new_role)
            session.commit()
            roles[role_data["name"]] = new_role
            print(f"✅ Đã tạo role {role_data['name']}")

    return roles


# Demo users data với thông tin đăng nhập đơn giản
demo_users = [
    {
        "username": "doctor",
        "email": "doctor@hms-psy.com",
        "full_name": "Bác sĩ Nguyễn Văn A",
        "password": "123456",
        "role_name": "doctor",
        "status": UserStatus.ACTIVE
    },
    {
        "username": "nurse",
        "email": "nurse@hms-psy.com",
        "full_name": "Y tá Trần Thị B",
        "password": "123456",
        "role_name": "nurse",
        "status": UserStatus.ACTIVE
    },
    {
        "username": "admin",
        "email": "admin@hms-psy.com",
        "full_name": "Quản trị viên hệ thống",
        "password": "123456",
        "role_name": "admin",
        "status": UserStatus.ACTIVE
    },
    {
        "username": "staff",
        "email": "staff@hms-psy.com",
        "full_name": "Nhân viên hành chính",
        "password": "123456",
        "role_name": "staff",
        "status": UserStatus.ACTIVE
    },
]

print("🌱 Bắt đầu tạo seed data cho users...")

# Tạo roles trước
print("\n📋 Tạo roles...")
roles = create_roles()

print("\n📋 Thông tin đăng nhập demo:")
print("   - Bác sĩ: doctor / 123456")
print("   - Y tá: nurse / 123456")
print("   - Quản trị: admin / 123456")
print("   - Nhân viên: staff / 123456")
print()

for user_data in demo_users:
    existing_user = session.query(User).filter_by(username=user_data["username"]).first()

    if existing_user:
        print(f"⚠️  User {user_data['username']} đã tồn tại")
    else:
        role = roles.get(user_data["role_name"])
        if not role:
            print(f"❌ Không tìm thấy role {user_data['role_name']}")
            continue

        new_user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash(user_data["password"]),
            role_id=role.id,
            status=user_data["status"]
        )
        session.add(new_user)
        session.commit()
        print(f"✅ Đã tạo user {user_data['username']} với vai trò {user_data['role_name']}")

session.close()
print("\n🎉 Hoàn thành tạo seed data cho users!")
