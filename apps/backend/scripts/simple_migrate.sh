#!/bin/bash

echo "🚀 Simple migration script..."

# Debug environment
echo "🔍 Environment: $ENVIRONMENT"
echo "🔍 DATABASE_URL: ${DATABASE_URL:0:50}..."

# Test database connection
echo "🔍 Testing database connection..."
python -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('Database connection OK')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed"
    exit 1
fi

echo "✅ Database connection successful"

# Run migration
echo "🔄 Running alembic upgrade head..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migration successful"
else
    echo "❌ Migration failed"
    exit 1
fi

echo "🎉 Migration completed!"
