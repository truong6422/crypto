import logging
import time
from datetime import datetime
from src.celery_app import celery_app
from src.database import get_session_local
from src.services.crypto_scraper import CryptoScraperService
from src.services.crypto_repository import CryptoRepository
from src.services.telegram_bot import TelegramService
from src.services.subscription_service import SubscriptionService
from src.constants import CryptoAssets, CryptoConfig
from src.models import CryptoHistory, CryptoDaily

logger = logging.getLogger(__name__)

@celery_app.task
def backfill_historical_data(symbol: str = None):
    """
    Tự động lấy dữ liệu lịch sử từ OKX (1m và 1D) nếu DB chưa đủ dữ liệu.
    """
    symbols = [symbol] if symbol else CryptoAssets.DEFAULT_IDS
    db = get_session_local()()
    
    try:
        for s in symbols:
            # 1. Backfill nến 1 phút (Để tính TA ngắn hạn)
            count_1m = db.query(CryptoHistory).filter(CryptoHistory.symbol == s).count()
            if count_1m < 50:
                logger.info(f"⏳ Backfill 300 nến 1m cho {s}...")
                candles = CryptoScraperService.get_historical_candles(s, bar="1m", limit=300)
                for c in candles:
                    db.add(CryptoHistory(
                        symbol=s, 
                        open=c["open"], high=c["high"], low=c["low"], 
                        close=c["close"], volume=c["volume"], 
                        timestamp=c["timestamp"]
                    ))
                db.commit()
                time.sleep(2) # Nghỉ để không bị rate limit
            
            # 2. Backfill nến 1 Ngày (Để xem xu hướng dài hạn)
            count_1d = db.query(CryptoDaily).filter(CryptoDaily.symbol == s).count()
            if count_1d < 10:
                logger.info(f"⏳ Backfill 100 nến 1D cho {s}...")
                candles = CryptoScraperService.get_historical_candles(s, bar="1D", limit=100)
                for c in candles:
                    db.add(CryptoDaily(
                        symbol=s, 
                        open=c["open"], high=c["high"], low=c["low"], 
                        close=c["close"], volume=c["volume"], 
                        timestamp=c["timestamp"]
                    ))
                db.commit()
                time.sleep(2)
                
    except Exception as e:
        logger.error(f"❌ Lỗi khi backfill dữ liệu: {e}")
        db.rollback()
    finally:
        db.close()

@celery_app.task
def update_daily_candles():
    """Cập nhật nến ngày định kỳ (mỗi giờ)."""
    db = get_session_local()()
    try:
        for s in CryptoAssets.DEFAULT_IDS:
            candles = CryptoScraperService.get_historical_candles(s, bar="1D", limit=1)
            if candles:
                c = candles[0]
                CryptoRepository.save_price(
                    db, s, c["close"], timeframe="1D", timestamp=c["timestamp"],
                    open_p=c["open"], high=c["high"], low=c["low"], volume=c["volume"]
                )
        logger.info("✅ Đã cập nhật nến ngày OHLCV cho các tài sản.")
    finally:
        db.close()

@celery_app.task
def crawl_and_save_prices():
    """Crawl nến 1m từ OKX, lưu vào DB và gửi cảnh báo nếu biến động mạnh."""
    # Đảm bảo có đủ dữ liệu lịch sử cho các chỉ số TA
    backfill_historical_data.delay()
    
    logger.info("🚀 Celery Task: Bắt đầu crawl dữ liệu OHLCV 1m...")
    db = get_session_local()()
    
    try:
        # Lấy danh sách mặc định + danh sách người dùng đăng ký
        subscribed_symbols = SubscriptionService.get_all_subscribed_symbols(db)
        symbols_to_crawl = list(set(CryptoAssets.DEFAULT_IDS + subscribed_symbols))
        
        for symbol in symbols_to_crawl:
            # Lấy nến 1m gần nhất từ OKX
            candles = CryptoScraperService.get_historical_candles(symbol, bar="1m", limit=2)
            if not candles:
                continue
            
            # Lấy nến vừa đóng (nến index 0 là nến cũ hơn, index 1 là nến mới nhất đang nhảy)
            # Thông thường OKX trả về nến mới nhất ở cuối list (get_historical_candles đã reverse lại)
            latest_candle = candles[-1]
            current_price = latest_candle["close"]
            
            # 1. Kiểm tra biến động (so với nến trước đó)
            if len(candles) > 1:
                prev_price = candles[-2]["close"]
                diff_pct = ((current_price - prev_price) / prev_price) * 100
                
                if abs(diff_pct) >= 1.0:
                    alert_msg = f"<b>⚠️ BIẾN ĐỘNG MẠNH: {symbol}</b>\n"
                    alert_msg += f"💰 Giá: ${current_price:,.2f} ({diff_pct:+.2f}%)\n"
                    
                    # Gửi cho admin mặc định (nếu có)
                    TelegramService.send_message(alert_msg)
                    
                    # Gửi cho những người đã đăng ký mã này
                    subs = db.query(UserSubscription).filter(
                        UserSubscription.symbol == symbol, 
                        UserSubscription.is_active == True
                    ).all()
                    for sub in subs:
                        if sub.chat_id != settings.TELEGRAM_CHAT_ID: # Tránh gửi trùng nếu chat_id là admin
                            TelegramService.send_message(alert_msg, chat_id=sub.chat_id)

            # 2. Lưu nến 1m với đầy đủ OHLCV
            CryptoRepository.save_price(
                db, 
                symbol=symbol, 
                price=current_price, 
                timeframe="1m", 
                timestamp=latest_candle["timestamp"],
                open_p=latest_candle["open"],
                high=latest_candle["high"],
                low=latest_candle["low"],
                volume=latest_candle["volume"]
            )
            
        logger.info(f"✨ Đã cập nhật dữ liệu nến 1m cho {len(CryptoAssets.DEFAULT_IDS)} đồng coin.")
        
    except Exception as e:
        logger.error(f"❌ Lỗi trong task crawl_and_save_prices: {e}")
    finally:
        db.close()

@celery_app.task
def send_periodic_report():
    """Gửi báo cáo thị trường định kỳ mỗi 10 phút."""
    logger.info("📊 Celery Task: Đang chuẩn bị báo cáo định kỳ...")
    db = get_session_local()()
    try:
        data = CryptoScraperService.get_prices()
        if not data:
            logger.warning("⚠️ Báo cáo định kỳ: Không lấy được giá từ OKX.")
            return

        logger.info(f"📈 Đã lấy được giá của {len(data)} đồng coin. Đang tính toán gợi ý...")

        message = "<b>📋 BÁO CÁO THỊ TRƯỜNG ĐỊNH KỲ</b>\n"
        message += f"<code>⏱ {datetime.now().strftime('%H:%M | %d/%m/%Y')}</code>\n"
        message += "━━━━━━━━━━━━━━━━━━\n\n"

        for coin in data:
            symbol = coin.get("instId")
            price = float(coin.get("last", 0))
            suggestion = CryptoRepository.get_investment_suggestion(db, symbol, price)
            
            message += f"🔸 <b>{symbol.replace('-USDT', '')}</b>: ${price:,.2f}\n"
            message += f"┗ 💡 {suggestion}\n"
            message += "──────────────────\n"

        success = TelegramService.send_message(message)
        if success:
            logger.info("✅ Đã gửi báo cáo định kỳ đến Telegram thành công.")
        else:
            logger.error("❌ Thất bại khi gửi báo cáo định kỳ qua Telegram Service.")
            
    except Exception as e:
        logger.error(f"❌ Lỗi nghiêm trọng trong task gửi báo cáo định kỳ: {e}", exc_info=True)
    finally:
        db.close()

@celery_app.task
def cleanup_old_prices():
    """Dọn dẹp dữ liệu cũ để bảo vệ server yếu."""
    logger.info("🧹 Celery Task: Đang dọn dẹp dữ liệu cũ...")
    db = get_session_local()()
    try:
        # Giữ nến 1m trong 2 ngày (đủ để xem chart ngắn hạn)
        count_1m = CryptoRepository.clear_old_data(db, hours=48, timeframe="1m")
        # Giữ nến 1D trong 90 ngày (đủ để xem xu hướng quý)
        count_1d = CryptoRepository.clear_old_data(db, hours=168*12, timeframe="1D") 
        logger.info(f"✅ Đã xóa {count_1m} nến 1m và {count_1d} nến 1D cũ.")
    except Exception as e:
        logger.error(f"❌ Lỗi khi dọn dẹp dữ liệu: {e}")
    finally:
        db.close()


@celery_app.task
def validate_signals_task():
    """Kiểm tra kết quả của các tín hiệu đã phát ra."""
    logger.info("🔍 Celery Task: Bắt đầu đối soát kết quả tín hiệu...")
    db = get_session_local()()
    try:
        count = CryptoRepository.validate_signals(db)
        logger.info(f"✅ Đã đối soát xong {count} tín hiệu.")
    except Exception as e:
        logger.error(f"❌ Lỗi khi đối soát tín hiệu: {e}")
    finally:
        db.close()


@celery_app.task
def record_predictions_task():
    """Tự động phân tích và lưu tín hiệu mỗi 5 phút."""
    logger.info("🤖 Celery Task: Bắt đầu tự động phân tích và ghi tín hiệu...")
    db = get_session_local()()
    try:
        data = CryptoScraperService.get_prices()
        if not data:
            return

        for coin in data:
            symbol = coin.get("instId")
            price = float(coin.get("last", 0))
            # Hàm này đã bao gồm logic record_signal bên trong
            CryptoRepository.get_investment_suggestion(db, symbol, price)
            
        logger.info("✅ Hoàn tất lượt tự động phân tích.")
    except Exception as e:
        logger.error(f"❌ Lỗi khi tự động phân tích tín hiệu: {e}")
    finally:
        db.close()
