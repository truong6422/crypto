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
def crawl_and_save_prices():
    """Task tự động lấy giá crypto, lưu vào database và cảnh báo biến động."""
    logger.info("🚀 Celery Task: Bắt đầu crawl giá crypto...")
    
    db = get_session_local()()
    try:
        # 1. Lấy dữ liệu từ OKX
        data = CryptoScraperService.get_prices()
        if not data:
            logger.warning("⚠️ Không lấy được dữ liệu từ OKX")
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
            
            # 3. Lưu vào database
            CryptoRepository.save_price(db, symbol, current_price)
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
        if not data: return

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

        TelegramService.send_message(message)
        logger.info("✅ Đã gửi báo cáo định kỳ thành công.")
    except Exception as e:
        logger.error(f"❌ Lỗi gửi báo cáo định kỳ: {e}")
    finally:
        db.close()

@celery_app.task
def cleanup_old_prices():
    """Dọn dẹp dữ liệu cũ (mặc định > 7 ngày)."""
    logger.info("🧹 Celery Task: Đang dọn dẹp dữ liệu cũ...")
    db = get_session_local()()
    try:
        count = CryptoRepository.clear_old_data(db, hours=CryptoConfig.DATA_RETENTION_HOURS)
        logger.info(f"✅ Đã xóa {count} bản ghi cũ.")
    except Exception as e:
        logger.error(f"❌ Lỗi khi dọn dẹp dữ liệu: {e}")
    finally:
        db.close()
