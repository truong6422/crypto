#!/usr/bin/env python3
"""
Script để reset database development PostgreSQL.
"""

import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env.development')

def reset_postgresql_database():
    """Reset database development PostgreSQL."""
    
    # Thông tin kết nối PostgreSQL
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DEV_DB_NAME = os.getenv("DB_NAME", "hms_psy_dev")
    
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
        
        # Drop database development nếu tồn tại
        try:
            cursor.execute(f"DROP DATABASE IF EXISTS {DEV_DB_NAME}")
            print(f"🗑️  Database PostgreSQL '{DEV_DB_NAME}' đã được xóa.")
        except Exception as e:
            print(f"⚠️  Lỗi khi xóa database: {e}")
        
        # Tạo lại database development
        try:
            cursor.execute(f"CREATE DATABASE {DEV_DB_NAME}")
            print(f"✅ Database PostgreSQL '{DEV_DB_NAME}' đã được tạo lại thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi tạo database: {e}")
            return False
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Lỗi kết nối PostgreSQL: {e}")
        print("💡 Hãy đảm bảo PostgreSQL đang chạy và có thể kết nối được.")
        return False
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return False

def main():
    """Reset database PostgreSQL."""
    print("🚀 Bắt đầu reset database development PostgreSQL...")
    
    success = reset_postgresql_database()
    if success:
        print("\n🎉 Hoàn thành reset database PostgreSQL!")
        print(f"📊 Dev DB: {os.getenv('DB_NAME', 'hms_psy_dev')}")
    else:
        print("\n❌ Reset database thất bại!")

if __name__ == "__main__":
    main() 