#!/bin/bash

# Script khởi động ứng dụng đơn giản

echo "🚀 Bắt đầu khởi động ứng dụng..."

# Debug environment
echo "🔍 Environment variables:"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   DATABASE_URL: ${DATABASE_URL:0:50}..."
echo "   REDIS_URL: $REDIS_URL"

# Chạy migrations
echo "📊 Chạy database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations thành công!"
else
    echo "❌ Migration thất bại"
fi

# Chạy seed data trong development
if [ "$ENVIRONMENT" != "production" ]; then
    echo "🌱 Chạy seed data (development mode)..."
    python scripts/seed_users_simple.py
else
    echo "🌱 Bỏ qua seed data (production mode)"
fi

# Khởi động ứng dụng
echo "🌐 Khởi động FastAPI server..."
exec uvicorn src.main:app --host 0.0.0.0 --port $PORT
