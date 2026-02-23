# Use official uv image for the binary
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# Use Python 3.12 slim image (match local dev)
FROM python:3.12-slim

# Copy uv binary
COPY --from=uv_bin /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        build-essential \
        python3-dev \
        postgresql-client \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from both apps
COPY apps/backend/requirements.txt ./backend-requirements.txt
COPY apps/telegram_bot/requirements.txt ./bot-requirements.txt

# Install all dependencies
RUN uv pip install --no-cache --system -r backend-requirements.txt
RUN uv pip install --no-cache --system -r bot-requirements.txt

# Copy all application code
COPY apps/ /app/apps/

# Create necessary directories
RUN mkdir -p static/avatars

# We don't use a single CMD because docker-compose will override it
# but we can provide a default for safety
CMD ["python3", "-m", "uvicorn", "apps.backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
