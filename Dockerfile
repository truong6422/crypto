# Giai đoạn 1: Build - Cài đặt dependencies và compile các thư viện nặng
FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.12-slim AS builder

COPY --from=uv_bin /uv /uvx /bin/

WORKDIR /app

# Cài đặt công cụ build cần thiết
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        build-essential \
        libpq-dev \
        libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file yêu cầu
COPY apps/backend/requirements.txt ./backend-requirements.txt
COPY apps/telegram_bot/requirements.txt ./bot-requirements.txt

# Tạo virtual environment và cài đặt thư viện vào đó
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN uv pip install --no-cache --prerelease=allow -r backend-requirements.txt
RUN uv pip install --no-cache --prerelease=allow -r bot-requirements.txt

# Giai đoạn 2: Runtime - Image siêu nhẹ để chạy ứng dụng
FROM python:3.12-slim

WORKDIR /app

# Chỉ cài đặt các thư viện runtime cần thiết (không có gcc/g++)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        libopenblas0 \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment từ stage builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH=/app

# Copy mã nguồn
COPY apps/ /app/apps/

# Tạo thư mục cần thiết
RUN mkdir -p static/avatars

# Mặc định sử dụng venv
CMD ["python3", "-m", "uvicorn", "apps.backend.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
