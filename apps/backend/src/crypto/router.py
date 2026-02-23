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
        
        # 1. Lưu vào lịch sử (Cập nhật dữ liệu cho gợi ý)
        CryptoRepository.save_price(db, symbol, price)
        
        # 2. Lấy gợi ý đầu tư và chỉ số thống kê
        suggestion = CryptoRepository.get_investment_suggestion(db, symbol, price)
        stats = CryptoRepository.get_price_stats(db, symbol, hours=24)
        
        coin["suggestion"] = suggestion
        coin["db_high_24h"] = stats["max"]
        coin["db_low_24h"] = stats["min"]
        enhanced_data.append(coin)
        
    # 3. Tự động dọn dẹp dữ liệu cũ (theo cấu hình)
    CryptoRepository.clear_old_data(db, hours=CryptoConfig.DATA_RETENTION_HOURS)
    
    return enhanced_data

@router.post("/crawl-and-notify", status_code=202)
async def crawl_and_notify(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Kích hoạt crawl giá và gửi thông báo qua Telegram."""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        raise HTTPException(status_code=400, detail="Telegram chưa được cấu hình.")

    background_tasks.add_task(perform_crawl_and_notify, db)
    return {"message": "Đang bắt đầu quá trình crawl và gửi thông báo..."}

async def perform_crawl_and_notify(db: Session):
    """Logic thực hiện crawl, lưu trữ và gửi tin nhắn."""
    data = CryptoScraperService.get_prices()
    if data:
        for coin in data:
            CryptoRepository.save_price(db, coin.get("instId"), float(coin.get("last", 0)))
            
        message = CryptoScraperService.format_price_message(data)
        TelegramService.send_message(message)
    else:
        TelegramService.send_message("❌ Lỗi: Không thể lấy dữ liệu crypto.")
