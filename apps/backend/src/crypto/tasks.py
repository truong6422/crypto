import logging
from datetime import datetime
from src.celery_app import celery_app
from src.database import get_session_local
from src.services.crypto_scraper import CryptoScraperService
from src.services.crypto_repository import CryptoRepository
from src.services.telegram_bot import TelegramService
from src.constants import CryptoAssets, CryptoConfig

logger = logging.getLogger(__name__)

@celery_app.task
def backfill_historical_data(symbol: str = None):
    """
    Tự động lấy dữ liệu lịch sử từ OKX (1m và 1D) nếu DB chưa đủ dữ liệu.
    """
    symbols = [symbol] if symbol else CryptoAssets.DEFAULT_IDS
    db = get_session_local()()
    
    try:
        from src.models import CryptoHistory, CryptoDaily
        import time
        
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
    """Crawl giá từ OKX, lưu vào DB và gửi cảnh báo nếu biến động mạnh."""
    # Đảm bảo có dữ liệu lịch sử trước khi crawl bản ghi mới
    backfill_historical_data.delay()
    
    logger.info("🚀 Celery Task: Bắt đầu crawl giá crypto...")
    db = get_session_local()()
    
    try:
        # 1. Lấy dữ liệu từ OKX
        data = CryptoScraperService.get_prices()
        if not data:
            logger.warning("⚠️ Không lấy được dữ liệu từ OKX.")
            return

        # 2. Xử lý từng đồng coin
        for coin in data:
            symbol = coin.get("instId")
            current_price = float(coin.get("last", 0))
            
            # --- KIỂM TRA BIẾN ĐỘNG MẠNH ---
            last_price = CryptoRepository.get_last_price(db, symbol)
            if last_price > 0:
                diff_pct = ((current_price - last_price) / last_price) * 100
                
                if abs(diff_pct) >= CryptoConfig.VOLATILITY_THRESHOLD_PCT:
                    direction = "📈 TĂNG" if diff_pct > 0 else "📉 GIẢM"
                    alert_msg = (
                        f"⚠️ <b>CẢNH BÁO BIẾN ĐỘNG MẠNH</b>\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🪙 Tài sản: <b>{symbol}</b>\n"
                        f"🔄 Trạng thái: <b>{direction} ĐỘT NGỘT</b>\n"
                        f"📊 Mức thay đổi: <code>{diff_pct:+.2f}%</code>\n"
                        f"💰 Giá hiện tại: <b>${current_price:,.2f}</b>\n"
                        f"🕒 Thời gian: {datetime.now().strftime('%H:%M:%S')}"
                    )
                    TelegramService.send_message(alert_msg)
                    logger.info(f"🔔 Đã gửi cảnh báo biến động cho {symbol}: {diff_pct:+.2f}%")
            
            logger.info(f"✅ Đã lưu giá {symbol}: ${current_price:,.2f}")
            
        logger.info(f"✨ Đã crawl và kiểm tra xong {len(data)} đồng coin.")
        
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
