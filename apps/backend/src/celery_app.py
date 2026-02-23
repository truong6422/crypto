from celery.schedules import crontab
from celery import Celery
from src.config import settings
from src.constants import CryptoConfig

# Khởi tạo Celery
celery_app = Celery(
    "crypto_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Cấu hình Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    # Tự động scan tasks trong các module
    imports=["src.crypto.tasks"]
)

# Cấu hình Celery Beat (Lập lịch)
celery_app.conf.beat_schedule = {
    "crawl-crypto-prices-every-1-minute": {
        "task": "src.crypto.tasks.crawl_and_save_prices",
        "schedule": CryptoConfig.CRAWL_INTERVAL_SECONDS,
    },
    "cleanup-old-crypto-data-daily": {
        "task": "src.crypto.tasks.cleanup_old_prices",
        "schedule": crontab(
            hour=CryptoConfig.CLEANUP_HOUR, 
            minute=CryptoConfig.CLEANUP_MINUTE
        ),
    },
    "send-periodic-report-every-10-minutes": {
        "task": "src.crypto.tasks.send_periodic_report",
        "schedule": CryptoConfig.REPORT_INTERVAL_SECONDS,
    },
    "update-daily-candles-every-hour": {
        "task": "src.crypto.tasks.update_daily_candles",
        "schedule": crontab(minute=0), # Chạy vào phút thứ 0 mỗi giờ
    }
}
