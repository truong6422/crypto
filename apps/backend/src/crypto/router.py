"""Router cho các tính năng liên quan đến Crypto."""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from ..services.crypto_scraper import CryptoScraperService
from ..services.telegram_bot import TelegramService
from ..services.crypto_repository import CryptoRepository
from ..database import get_db
from ..config import settings
from ..constants import CryptoConfig

router = APIRouter()

@router.get("/prices")
async def get_prices(db: Session = Depends(get_db)):
    """Lấy giá crypto hiện tại kèm gợi ý đầu tư."""
    data = CryptoScraperService.get_prices()
    if not data:
        raise HTTPException(status_code=503, detail="Không thể lấy dữ liệu từ OKX")
    
    enhanced_data = []
    for coin in data:
        symbol = coin.get("instId")
        price = float(coin.get("last", 0))
        
        # Lấy gợi ý đầu tư và chỉ số thống kê từ DB (dữ liệu đã được Celery cập nhật)
        suggestion = CryptoRepository.get_investment_suggestion(db, symbol, price)
        stats = CryptoRepository.get_price_stats(db, symbol, hours=24)
        
        coin["suggestion"] = suggestion
        coin["db_high_24h"] = stats["max"]
        coin["db_low_24h"] = stats["min"]
        enhanced_data.append(coin)
    
    return enhanced_data

@router.post("/crawl-and-notify", status_code=202)
async def crawl_and_notify(background_tasks: BackgroundTasks):
    """Kích hoạt crawl giá và gửi thông báo qua Telegram."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=400, detail="Telegram chưa được cấu hình.")

    from ..crypto.tasks import crawl_and_save_prices, send_periodic_report
    crawl_and_save_prices.delay()
    send_periodic_report.delay()
    return {"message": "Đã kích hoạt các tác vụ ngầm để cập nhật giá và gửi báo cáo."}


@router.get("/accuracy")
async def get_accuracy(db: Session = Depends(get_db)):
    """Lấy báo cáo độ chính xác của các dự đoán."""
    report = CryptoRepository.get_accuracy_report(db)
    return {"report": report}
