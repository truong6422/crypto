# Use official uv image for the binary
FROM ghcr.io/astral-sh/uv:latest AS uv_bin

# Use Python 3.11 slim image
FROM python:3.11-slim

# Copy uv binary
COPY --from=uv_bin /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
# uv specific optimizations
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies using uv
COPY apps/backend/requirements.txt .
RUN uv pip install --no-cache --system -r requirements.txt

# Copy backend code
COPY apps/backend/ .

# Create static directory if it doesn't exist
RUN mkdir -p static/avatars

# Copy startup script
COPY apps/backend/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port
EXPOSE $PORT

# Run the startup script
CMD ["sh", "/app/start.sh"]

