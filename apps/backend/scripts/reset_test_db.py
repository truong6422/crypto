#!/usr/bin/env python3
"""
Script để reset database test PostgreSQL.
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('env.development')

def reset_test_database():
    """Reset database test PostgreSQL."""
    
    # Thông tin kết nối PostgreSQL
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_USER = "postgres"
    DB_PASSWORD = "postgres"
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
        
        # Drop database test nếu tồn tại
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}")
            print(f"🗑️  Database '{TEST_DB_NAME}' đã được xóa.")
        except Exception as e:
            print(f"⚠️  Lỗi khi xóa database: {e}")
        
        # Tạo lại database test
        try:
            cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
            print(f"✅ Database '{TEST_DB_NAME}' đã được tạo lại thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi tạo database: {e}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Hoàn thành reset database test!")
        print(f"🧪 Test DB: {TEST_DB_NAME}")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Lỗi kết nối PostgreSQL: {e}")
        print("💡 Hãy đảm bảo PostgreSQL đang chạy và có thể kết nối được.")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")

if __name__ == "__main__":
    print("🚀 Bắt đầu reset database test PostgreSQL...")
    reset_test_database() 