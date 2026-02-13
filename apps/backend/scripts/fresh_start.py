#!/usr/bin/env python3
"""
Script để reset hoàn toàn database và chạy lại seed data.
Sử dụng cho development khi cần fresh start.
"""

import os
import sys
import subprocess


def run_script(script_name: str, description: str):
    """Chạy một script."""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")

    script_path = os.path.join(os.path.dirname(__file__), script_name)

    try:
        result = subprocess.run([sys.executable, script_path],
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print(f"✅ {description} - Thành công!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Thất bại!")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Reset database và chạy seed data."""
    print("🚀 Bắt đầu fresh start - Reset database và seed data...")

    # Danh sách script cần chạy theo thứ tự
    scripts = [
        ("reset_dev_db.py", "Reset database development"),
        ("seed_all.py", "Chạy migration và seed data"),
    ]

    success_count = 0
    total_scripts = len(scripts)

    for script_name, description in scripts:
        if run_script(script_name, description):
            success_count += 1
        else:
            print(f"\n⚠️  Dừng quá trình do lỗi ở: {description}")
            break

    print(f"\n{'='*60}")
    print("📊 KẾT QUẢ FRESH START")
    print(f"{'='*60}")
    print(f"✅ Thành công: {success_count}/{total_scripts}")
    print(f"❌ Thất bại: {total_scripts - success_count}/{total_scripts}")

    if success_count == total_scripts:
        print("\n🎉 Fresh start hoàn thành thành công!")
        print("\n📋 Đã thực hiện:")
        print("   - Xóa database cũ")
        print("   - Tạo database mới")
        print("   - Chạy migration tạo schema")
        print("   - Seed dữ liệu mẫu")
        print("\n💡 Database đã sẵn sàng để sử dụng!")
        return True
    else:
        print("\n⚠️  Fresh start thất bại. Vui lòng kiểm tra lỗi và chạy lại.")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
