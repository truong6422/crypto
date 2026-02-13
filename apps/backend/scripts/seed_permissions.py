#!/usr/bin/env python3
"""
Script tạo permissions cơ bản cho hệ thống.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.auth.models import Role, Permission
from src.config import settings
from src.models import BaseModel

db_url = settings.DATABASE_URL
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Create tables if they don't exist
BaseModel.metadata.create_all(bind=engine)

print("🌱 Bắt đầu tạo seed data cho permissions...")

# Định nghĩa permissions cơ bản
permissions_data = [
    # User Management
    {"name": "VIEW_USERS", "description": "Xem danh sách người dùng"},
    {"name": "CREATE_USERS", "description": "Tạo người dùng mới"},
    {"name": "UPDATE_USERS", "description": "Cập nhật thông tin người dùng"},
    {"name": "DELETE_USERS", "description": "Xóa người dùng"},
    {"name": "TOGGLE_USER_STATUS", "description": "Kích hoạt/vô hiệu hóa người dùng"},

    # Role Management
    {"name": "VIEW_ROLES", "description": "Xem danh sách vai trò"},
    {"name": "CREATE_ROLES", "description": "Tạo vai trò mới"},
    {"name": "UPDATE_ROLES", "description": "Cập nhật vai trò"},
    {"name": "DELETE_ROLES", "description": "Xóa vai trò"},

    # Permission Management
    {"name": "VIEW_PERMISSIONS", "description": "Xem danh sách quyền"},
    {"name": "CREATE_PERMISSIONS", "description": "Tạo quyền mới"},
    {"name": "UPDATE_PERMISSIONS", "description": "Cập nhật quyền"},
    {"name": "DELETE_PERMISSIONS", "description": "Xóa quyền"},

    # Patient Management
    {"name": "VIEW_PATIENTS", "description": "Xem danh sách bệnh nhân"},
    {"name": "CREATE_PATIENTS", "description": "Tạo hồ sơ bệnh nhân mới"},
    {"name": "UPDATE_PATIENTS", "description": "Cập nhật thông tin bệnh nhân"},
    {"name": "DELETE_PATIENTS", "description": "Xóa hồ sơ bệnh nhân"},

    # Medical Records
    {"name": "VIEW_MEDICAL_RECORDS", "description": "Xem hồ sơ y tế"},
    {"name": "CREATE_MEDICAL_RECORDS", "description": "Tạo hồ sơ y tế mới"},
    {"name": "UPDATE_MEDICAL_RECORDS", "description": "Cập nhật hồ sơ y tế"},
    {"name": "DELETE_MEDICAL_RECORDS", "description": "Xóa hồ sơ y tế"},

    # Appointments
    {"name": "VIEW_APPOINTMENTS", "description": "Xem lịch hẹn"},
    {"name": "CREATE_APPOINTMENTS", "description": "Tạo lịch hẹn mới"},
    {"name": "UPDATE_APPOINTMENTS", "description": "Cập nhật lịch hẹn"},
    {"name": "DELETE_APPOINTMENTS", "description": "Xóa lịch hẹn"},

    # Prescriptions
    {"name": "VIEW_PRESCRIPTIONS", "description": "Xem đơn thuốc"},
    {"name": "CREATE_PRESCRIPTIONS", "description": "Tạo đơn thuốc mới"},
    {"name": "UPDATE_PRESCRIPTIONS", "description": "Cập nhật đơn thuốc"},
    {"name": "DELETE_PRESCRIPTIONS", "description": "Xóa đơn thuốc"},

    # Inventory
    {"name": "VIEW_INVENTORY", "description": "Xem kho thuốc"},
    {"name": "CREATE_INVENTORY", "description": "Thêm thuốc vào kho"},
    {"name": "UPDATE_INVENTORY", "description": "Cập nhật thông tin thuốc"},
    {"name": "DELETE_INVENTORY", "description": "Xóa thuốc khỏi kho"},

    # Reports
    {"name": "VIEW_REPORTS", "description": "Xem báo cáo"},
    {"name": "CREATE_REPORTS", "description": "Tạo báo cáo mới"},
    {"name": "EXPORT_REPORTS", "description": "Xuất báo cáo"},

    # System Settings
    {"name": "VIEW_SYSTEM_SETTINGS", "description": "Xem cài đặt hệ thống"},
    {"name": "UPDATE_SYSTEM_SETTINGS", "description": "Cập nhật cài đặt hệ thống"},

    # Health Monitoring
    {"name": "VIEW_HEALTH_MONITORING", "description": "Xem giám sát sức khỏe"},
    {"name": "CREATE_HEALTH_MONITORING", "description": "Tạo bản ghi giám sát sức khỏe"},
    {"name": "UPDATE_HEALTH_MONITORING", "description": "Cập nhật giám sát sức khỏe"},
]

# Tạo permissions
created_permissions = []
for perm_data in permissions_data:
    # Kiểm tra permission đã tồn tại chưa
    existing_perm = session.query(Permission).filter(
        Permission.name == perm_data["name"],
        Permission.is_deleted == False
    ).first()

    if not existing_perm:
        permission = Permission(
            name=perm_data["name"],
            description=perm_data["description"],
            is_active=True
        )
        session.add(permission)
        created_permissions.append(permission)
        print(f"   ✅ Tạo permission: {perm_data['name']}")
    else:
        print(f"   ⚠️  Permission đã tồn tại: {perm_data['name']}")

session.commit()

print(f"\n📊 Tổng số permissions đã tạo: {len(created_permissions)}")

# Gán permissions cho roles
print("\n🔗 Gán permissions cho roles...")

# Lấy roles hiện có
roles = session.query(Role).filter(Role.is_deleted == False).all()
role_dict = {role.name: role for role in roles}

# Định nghĩa permissions cho từng role
role_permissions = {
    "admin": [
        # Tất cả permissions
        "VIEW_USERS", "CREATE_USERS", "UPDATE_USERS", "DELETE_USERS", "TOGGLE_USER_STATUS",
        "VIEW_ROLES", "CREATE_ROLES", "UPDATE_ROLES", "DELETE_ROLES",
        "VIEW_PERMISSIONS", "CREATE_PERMISSIONS", "UPDATE_PERMISSIONS", "DELETE_PERMISSIONS",
        "VIEW_PATIENTS", "CREATE_PATIENTS", "UPDATE_PATIENTS", "DELETE_PATIENTS",
        "VIEW_MEDICAL_RECORDS", "CREATE_MEDICAL_RECORDS", "UPDATE_MEDICAL_RECORDS", "DELETE_MEDICAL_RECORDS",
        "VIEW_APPOINTMENTS", "CREATE_APPOINTMENTS", "UPDATE_APPOINTMENTS", "DELETE_APPOINTMENTS",
        "VIEW_PRESCRIPTIONS", "CREATE_PRESCRIPTIONS", "UPDATE_PRESCRIPTIONS", "DELETE_PRESCRIPTIONS",
        "VIEW_INVENTORY", "CREATE_INVENTORY", "UPDATE_INVENTORY", "DELETE_INVENTORY",
        "VIEW_REPORTS", "CREATE_REPORTS", "EXPORT_REPORTS",
        "VIEW_SYSTEM_SETTINGS", "UPDATE_SYSTEM_SETTINGS",
        "VIEW_HEALTH_MONITORING", "CREATE_HEALTH_MONITORING", "UPDATE_HEALTH_MONITORING",
    ],
    "doctor": [
        # Permissions cho bác sĩ
        "VIEW_PATIENTS", "CREATE_PATIENTS", "UPDATE_PATIENTS",
        "VIEW_MEDICAL_RECORDS", "CREATE_MEDICAL_RECORDS", "UPDATE_MEDICAL_RECORDS",
        "VIEW_APPOINTMENTS", "CREATE_APPOINTMENTS", "UPDATE_APPOINTMENTS",
        "VIEW_PRESCRIPTIONS", "CREATE_PRESCRIPTIONS", "UPDATE_PRESCRIPTIONS",
        "VIEW_INVENTORY", "UPDATE_INVENTORY",
        "VIEW_REPORTS", "CREATE_REPORTS", "EXPORT_REPORTS",
        "VIEW_HEALTH_MONITORING", "CREATE_HEALTH_MONITORING", "UPDATE_HEALTH_MONITORING",
    ],
    "nurse": [
        # Permissions cho y tá
        "VIEW_PATIENTS", "UPDATE_PATIENTS",
        "VIEW_MEDICAL_RECORDS", "UPDATE_MEDICAL_RECORDS",
        "VIEW_APPOINTMENTS", "UPDATE_APPOINTMENTS",
        "VIEW_PRESCRIPTIONS", "UPDATE_PRESCRIPTIONS",
        "VIEW_INVENTORY", "UPDATE_INVENTORY",
        "VIEW_REPORTS",
        "VIEW_HEALTH_MONITORING", "CREATE_HEALTH_MONITORING", "UPDATE_HEALTH_MONITORING",
    ],
    "staff": [
        # Permissions cho nhân viên
        "VIEW_PATIENTS",
        "VIEW_MEDICAL_RECORDS",
        "VIEW_APPOINTMENTS", "CREATE_APPOINTMENTS",
        "VIEW_INVENTORY",
        "VIEW_REPORTS",
        "VIEW_HEALTH_MONITORING",
    ]
}

# Gán permissions cho từng role
for role_name, permission_names in role_permissions.items():
    if role_name in role_dict:
        role = role_dict[role_name]

        # Lấy permissions theo tên
        permissions = session.query(Permission).filter(
            Permission.name.in_(permission_names),
            Permission.is_deleted == False
        ).all()

        # Gán permissions cho role
        role.permissions = permissions
        print(f"   ✅ Gán {len(permissions)} permissions cho role: {role_name}")
    else:
        print(f"   ❌ Không tìm thấy role: {role_name}")

session.commit()

print("\n🎉 Hoàn thành tạo seed data cho permissions!")
print("\n📋 Tóm tắt:")
print(f"   - Tổng số permissions: {len(permissions_data)}")
print(f"   - Tổng số roles: {len(roles)}")
for role_name, permission_names in role_permissions.items():
    if role_name in role_dict:
        print(f"   - Role '{role_name}': {len(permission_names)} permissions")

session.close()
