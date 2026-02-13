# Makefile for Crypto Base

.PHONY: help run-bot run-backend run-frontend install

help:
	@echo "Các lệnh có sẵn:"
	@echo "  make run-bot      - Chạy Telegram Bot"
	@echo "  make run-backend  - Chạy FastAPI Backend"
	@echo "  make run-frontend - Chạy React Frontend"
	@echo "  make install      - Cài đặt dependencies cho toàn bộ dự án"

run-bot:
	@echo "🚀 Đang khởi động Telegram Bot..."
	@PYTHONPATH=$${PYTHONPATH}:$(shell pwd) ./apps/telegram_bot/venv/bin/python3 apps/telegram_bot/main.py

run-backend:
	@echo "🚀 Đang khởi động Backend..."
	@cd apps/backend && ./venv/bin/python3 -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

run-frontend:
	@echo "🚀 Đang khởi động Frontend..."
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
