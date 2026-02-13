#!/usr/bin/env python3
"""
Script để tạo database PostgreSQL cho ứng dụng HMS PSY.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_database():
    """Tạo database PostgreSQL."""

    # Thông tin kết nối PostgreSQL
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"

    # Tên database cần tạo
    DEV_DB_NAME = "hms_psy_dev"
    TEST_DB_NAME = "hms_psy_test"

    try:
        # Kết nối đến PostgreSQL server
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Tạo database development
        try:
            cursor.execute(f"CREATE DATABASE {DEV_DB_NAME}")
            print(f"✅ Database '{DEV_DB_NAME}' đã được tạo thành công!")
        except psycopg2.errors.DuplicateDatabase:
            print(f"⚠️  Database '{DEV_DB_NAME}' đã tồn tại.")

        # Tạo database test
        try:
            cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
            print(f"✅ Database '{TEST_DB_NAME}' đã được tạo thành công!")
        except psycopg2.errors.DuplicateDatabase:
            print(f"⚠️  Database '{TEST_DB_NAME}' đã tồn tại.")

        cursor.close()
        conn.close()

        print("\n🎉 Hoàn thành tạo database PostgreSQL!")
        print(f"📊 Development DB: {DEV_DB_NAME}")
        print(f"🧪 Test DB: {TEST_DB_NAME}")

    except psycopg2.OperationalError as e:
        print(f"❌ Lỗi kết nối PostgreSQL: {e}")
        print("💡 Hãy đảm bảo PostgreSQL đang chạy và có thể kết nối được.")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")

if __name__ == "__main__":
    print("🚀 Bắt đầu tạo database PostgreSQL...")
    create_database()
