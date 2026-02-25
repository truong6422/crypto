"""Router cho các tính năng liên quan đến Crypto."""
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from ..services.crypto_scraper import CryptoScraperService
from ..services.telegram_bot import TelegramService
from ..services.crypto_repository import CryptoRepository
from ..services.subscription_service import SubscriptionService
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


@router.get("/search")
async def search_coins(q: str):
    """Tìm kiếm mã coin trên OKX."""
    results = CryptoScraperService.search_instruments(q)
    return results[:10]  # Giới hạn 10 kết quả


@router.post("/subscribe")
async def subscribe(chat_id: str, symbol: str, db: Session = Depends(get_db)):
    """Đăng ký nhận thông báo cho 1 mã coin."""
    # Kiểm tra mã có tồn tại trên OKX không
    instruments = CryptoScraperService.get_all_instruments()
    valid_symbols = [inst["instId"] for inst in instruments]
    
    # Chuẩn hóa
    if not symbol.endswith("-USDT") and "-" not in symbol:
        symbol = f"{symbol.upper()}-USDT"
        
    if symbol not in valid_symbols:
        raise HTTPException(status_code=400, detail=f"Mã {symbol} không hợp lệ trên OKX SPOT.")
        
    sub = SubscriptionService.subscribe(db, chat_id, symbol)
    
    # Trigger backfill dữ liệu lịch sử ngay lập tức để có thể phân tích
    from .tasks import backfill_historical_data
    backfill_historical_data.delay(symbol)
    
    return {"message": f"Đã đăng ký theo dõi {symbol}", "sub_id": sub.id}


@router.post("/unsubscribe")
async def unsubscribe(chat_id: str, symbol: str, db: Session = Depends(get_db)):
    """Hủy đăng ký nhận thông báo."""
    success = SubscriptionService.unsubscribe(db, chat_id, symbol)
    if not success:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông tin đăng ký.")
    return {"message": f"Đã hủy đăng ký theo dõi {symbol}"}


@router.get("/subscriptions")
async def list_subscriptions(chat_id: str, db: Session = Depends(get_db)):
    """Lấy danh sách đăng ký của một chat_id."""
    subs = SubscriptionService.get_user_subscriptions(db, chat_id)
    return [s.symbol for s in subs]
