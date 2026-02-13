# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create static directory if it doesn't exist
RUN mkdir -p static/avatars

# Create a startup script that runs migration before starting the app
RUN echo '#!/bin/bash\n\
echo "🚀 Starting application with migration..."\n\
\n\
# Test database connection\n\
echo "🔍 Testing database connection..."\n\
python -c "\n\
import os\n\
from sqlalchemy import create_engine, text\n\
try:\n\
    engine = create_engine(os.getenv(\"DATABASE_URL\"))\n\
    with engine.connect() as conn:\n\
        conn.execute(text(\"SELECT 1\"))\n\
    print(\"Database connection OK\")\n\
except Exception as e:\n\
    print(f\"Database connection failed: {e}\")\n\
    exit(1)\n\
"\n\
\n\
if [ $? -ne 0 ]; then\n\
    echo "❌ Database connection failed"\n\
    exit 1\n\
fi\n\
\n\
echo "✅ Database connection successful"\n\
\n\
# Run migration\n\
echo "🔄 Running alembic upgrade head..."\n\
alembic upgrade head\n\
\n\
if [ $? -eq 0 ]; then\n\
    echo "✅ Migration successful"\n\
else\n\
    echo "❌ Migration failed"\n\
    exit 1\n\
fi\n\
\n\
# Seed demo data if needed\n\
if [ "$SEED_DEMO_DATA" = "true" ]; then\n\
    echo "🌱 Seeding demo data..."\n\
    python scripts/seed_demo_users.py\n\
    if [ $? -eq 0 ]; then\n\
        echo "✅ Demo data seeded successfully"\n\
    else\n\
        echo "⚠️ Demo data seeding failed, but continuing..."\n\
    fi\n\
fi\n\
\n\
echo "🎉 Starting application..."\n\
exec gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE $PORT

# Run the startup script
CMD ["/app/start.sh"]
