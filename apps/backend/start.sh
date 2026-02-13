#!/bin/bash

set -e

echo "🚀 Starting Daily Meals Backend..."

# Use PYTHONPATH to ensure imports work correctly
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
# pg_isready is more reliable than sleep 5
# Assuming the host is 'db' as defined in docker-compose.yml
until pg_isready -h db -p 5432 -U postgres; do
  echo "⌛ Database is unavailable - sleeping"
  sleep 1
done

echo "✅ Database is up and running!"

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

# Run master data seed first (Categories & Calories)
echo "🌱 Running master data seed..."
python scripts/seed_categories.py || echo "⚠️ Warning: seed_categories.py failed"
python scripts/seed_food_master.py || echo "⚠️ Warning: seed_food_master.py failed"

# Run demo users seed
echo "🌱 Running demo users seed..."
python scripts/seed_demo_users.py || echo "⚠️ Warning: seed_demo_users.py failed"

# Start the application
echo "🚀 Starting application..."
exec gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT

