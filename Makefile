# Makefile for Crypto Base

.PHONY: help run-bot run-backend run-frontend install bot dev makemigrations migrate run-worker run-beat run-flower redis-restart

help:
	@echo "Các lệnh có sẵn:"
	@echo "  make dev          - Chạy cả Backend và Bot (Development)"
	@echo "  make makemigrations - Tạo file migration mới tự động (001, 002...)"
	@echo "  make migrate      - Cập nhật database lên bản mới nhất"
	@echo "  make run-bot      - Chạy Telegram Bot"
	@echo "  make bot          - Shortcut chạy Telegram Bot"
	@echo "  make run-backend  - Chạy FastAPI Backend"
	@echo "  make run-worker   - Chạy Celery Worker"
	@echo "  make run-beat     - Chạy Celery Beat"
	@echo "  make run-flower   - Chạy Celery Flower (Monitor UI)"
	@echo "  make run-frontend - Chạy React Frontend"
	@echo "  make install      - Cài đặt dependencies cho toàn bộ dự án"

dev: redis-restart
	@npx concurrently "make run-backend" "make run-bot" "make run-worker" "make run-beat" "make run-flower"

redis-restart:
	@echo "🔄 Đang khởi động lại Redis..."
	@sudo systemctl restart redis-server

makemigrations:
	@cd apps/backend && ./venv/bin/python3 scripts/makemigrations.py

migrate:
	@cd apps/backend && ./venv/bin/alembic upgrade head

bot: run-bot

run-bot:
	@echo "🚀 Đang khởi động Telegram Bot..."
	@PYTHONPATH=$${PYTHONPATH}:$(shell pwd) ./apps/telegram_bot/venv/bin/python3 apps/telegram_bot/main.py

run-backend:
	@echo "🚀 Đang khởi động Backend..."
	@cd apps/backend && ./venv/bin/python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8005

run-worker:
	@echo "🚀 Đang khởi động Celery Worker (Lite Mode)..."
	@cd apps/backend && PYTHONPATH=. ./venv/bin/celery -A src.celery_app:celery_app worker --loglevel=info --concurrency=1

run-beat:
	@echo "🚀 Đang khởi động Celery Beat..."
	@cd apps/backend && PYTHONPATH=. ./venv/bin/celery -A src.celery_app:celery_app beat --loglevel=info

run-flower:
	@echo "🚀 Đang khởi động Celery Flower (http://localhost:5555)..."
	@cd apps/backend && PYTHONPATH=. ./venv/bin/celery -A src.celery_app:celery_app flower --port=5555

run-frontend:
	@echo "🚀 Đang khởi động Frontend (Vite Dev - Cảnh báo: Ngốn RAM)..."
	@cd apps/frontend && npm run dev

install:
	@echo "📦 Đang cài đặt dependencies..."
	@echo "--- Telegram Bot ---"
	@cd apps/telegram_bot && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	@echo "--- Backend ---"
	@cd apps/backend && python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
	@echo "--- Frontend ---"
	@cd apps/frontend && npm install
	@echo "✅ Đã cài đặt xong tất cả!"
