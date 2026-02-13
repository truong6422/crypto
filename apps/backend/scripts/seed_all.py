#!/usr/bin/env python3
"""
Script chạy tất cả các script seed data.
"""

import os
import subprocess
import sys

from src.config import settings


def run_migration():
    """Chạy migration để tạo schema database."""
    print(f"\n{'=' * 60}")
    print(f"🔄 Chạy database migration...")
    print(f"{'=' * 60}")
    print(settings.BASE_DIR)

    try:
        # Chạy alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True,
            cwd=settings.BASE_DIR
        )
        print(result.stdout)
        print("✅ Migration - Thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration - Thất bại!")
        print(f"Error: {e.stderr}")
        return False


def run_script(script_name: str, description: str):
    """Chạy một script seed."""
    print(f"\n{'=' * 60}")
    print(f"🌱 {description}")
    print(f"{'=' * 60}")

    script_path = os.path.join(os.path.dirname(__file__), script_name)

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, check=True
        )
        print(result.stdout)
        print(f"✅ {description} - Thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Thất bại!")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Chạy migration và tất cả script seed."""
    print("🚀 Bắt đầu setup database và chạy seed data...")

    # Chạy migration trước
    if not run_migration():
        print("\n⚠️  Migration thất bại. Dừng quá trình seed.")
        return False

    # Danh sách script cần chạy theo thứ tự
    scripts = [
        ("seed_categories.py", "Tạo các danh mục cơ bản"),
        ("seed_food_master.py", "Tạo dữ liệu thực phẩm (calo)"),
        ("seed_users.py", "Tạo dữ liệu người dùng mẫu"),
        ("seed_permissions.py", "Tạo permissions và gán cho roles"),
    ]

    success_count = 0
    total_scripts = len(scripts)

    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"\n⚠️  Dừng chạy script do lỗi ở: {description}")
            break

    print(f"\n{'=' * 60}")
    print("📊 KẾT QUẢ CHẠY SCRIPT SEED")
    print(f"{'=' * 60}")
    print(f"✅ Thành công: {success_count}/{total_scripts}")
    print(f"❌ Thất bại: {total_scripts - success_count}/{total_scripts}")

    if success_count == total_scripts:
        print("\n🎉 Tất cả script seed đã chạy thành công!")
        print("\n📋 Dữ liệu đã được tạo:")
        print("   - Database schema (từ migration)")
        print("   - Users: admin, doctor, nurse, staff")
        print("   - Roles: admin, doctor, nurse, staff")
        print("   - Permissions: 41 permissions cơ bản")
        print("   - Role-Permission mappings")
        print("\n💡 Bạn có thể bắt đầu sử dụng ứng dụng!")
        return True
    else:
        print("\n⚠️  Một số script seed đã thất bại. Vui lòng kiểm tra lỗi và chạy lại.")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
