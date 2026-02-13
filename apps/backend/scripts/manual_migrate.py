#!/usr/bin/env python3
"""
Script để chạy migration thủ công với debug chi tiết
"""

import os
import sys
from sqlalchemy import create_engine, text
from alembic import command
from alembic.config import Config

def main():
    print("🚀 Bắt đầu manual migration...")
    
    # Debug environment
    print(f"🔍 Environment: {os.getenv('ENVIRONMENT', 'NOT_SET')}")
    print(f"🔍 DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT_SET')[:50]}...")
    
    # Test database connection
    print("🔍 Testing database connection...")
    try:
        engine = create_engine(os.getenv('DATABASE_URL'))
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1
    
    # Check current tables
    print("🔍 Checking current tables...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"Current tables: {tables}")
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return 1
    
    # Check alembic version
    print("🔍 Checking alembic version...")
    try:
        with engine.connect() as conn:
            result = conn.execute(text('SELECT version_num FROM alembic_version'))
            current_version = result.scalar()
            print(f"Current alembic version: {current_version}")
    except Exception as e:
        print(f"⚠️  No alembic_version table: {e}")
        print("This means migrations haven't been run yet")
    
    # Run migrations
    print("🔄 Running alembic upgrade head...")
    try:
        # Set up alembic config
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "migrations")
        
        # Run upgrade
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully!")
        
        # Check tables again
        print("🔍 Checking tables after migration...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"Tables after migration: {tables}")
            
            # Check alembic version
            result = conn.execute(text('SELECT version_num FROM alembic_version'))
            current_version = result.scalar()
            print(f"Final alembic version: {current_version}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
