import logging
import os
import sys
import httpx
import datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Thêm đường dẫn để có thể import từ backend nếu cần
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# Load biến môi trường từ apps/backend/.env
env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /start"""
    await update.message.reply_text("Bot đã sẵn sàng! Các lệnh có sẵn:\n/crypto - Xem giá crypto (OKX)\n/check - Xem tỷ lệ thắng của Robot\nping - Kiểm tra kết nối")

async def get_crypto_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /crypto"""
    await update.message.reply_text("⏳ Đang lấy giá thực tế từ sàn OKX...")
    
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_url}/api/crypto/prices", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not isinstance(data, list):
                await update.message.reply_text("❌ Dữ liệu từ Backend không đúng định dạng.")
                return

            message = "<b>💎 CRYPTO DASHBOARD SIGNAL</b>\n"
            message += "<code>━━━━━━━━━━━━━━━━━━━━━━</code>\n\n"
            
            # Map icon cho từng đồng coin
            coin_icons = {
                "BTC": "🟠",
                "ETH": "🔹",
                "SOL": "☀️",
                "BNB": "🔶",
            }
            
            for coin in data:
                raw_id = coin.get("instId", "Unknown")
                symbol = raw_id.replace("-USDT", "")
                icon = coin_icons.get(symbol, "🪙")
                
                last_price = float(coin.get("last", 0))
                open_24h = float(coin.get("open24h", 0))
                suggestion = coin.get("suggestion", "N/A")
                
                # Database stats
                db_high = coin.get("db_high_24h", 0)
                db_low = coin.get("db_low_24h", 0)
                
                change_pct = ((last_price - open_24h) / open_24h * 100) if open_24h > 0 else 0
                
                # Xác định icon xu hướng
                if change_pct > 3: trend_label = "🚀 Moon"
                elif change_pct > 0: trend_label = "📈 Up"
                elif change_pct < -3: trend_label = "☄️ Dump"
                else: trend_label = "📉 Down"
                
                status_color = "🟢" if change_pct >= 0 else "🔴"
                
                message += f"{icon} <b>{symbol}/USDT</b> | {trend_label}\n"
                message += f"┣ 💵 Giá: <b>${last_price:,.2f}</b>\n"
                message += f"┣ 📊 Biến động: <code>{change_pct:+.2f}%</code> {status_color}\n"
                
                if db_high > 0:
                    message += f"┣ 📏 Range: <code>${db_low:,.1f}</code>–<code>${db_high:,.1f}</code>\n"
                
                message += f"┗ 💡 {suggestion}\n"
                message += "<code>──────────────────────</code>\n"
            
            message += f"<b>⏰ {datetime.datetime.now().strftime('%H:%M:%S | %d/%m/%Y')}</b>"
            await update.message.reply_text(message, parse_mode="HTML")
            
    except Exception as e:
        logger.error(f"Lỗi khi xử lý lệnh /crypto: {e}")
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

async def accuracy_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý lệnh /check để xem độ chính xác tín hiệu."""
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8001")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{backend_url}/api/crypto/accuracy", timeout=10)
            response.raise_for_status()
            data = response.json()
            report = data.get("report", "Không có dữ liệu báo cáo.")
            await update.message.reply_text(report, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Lỗi khi xử lý lệnh /check: {e}")
        await update.message.reply_text("❌ Không thể lấy dữ liệu thống kê từ hệ thống.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xử lý tin nhắn văn bản"""
    text = update.message.text.lower().strip()
    
    if text == "ping":
        logger.info(f"Nhận được ping từ {update.effective_user.id}")
        await update.message.reply_text("pong")
    elif text == "check id":
        await update.message.reply_text(f"Chat ID của bạn là: {update.effective_chat.id}")

if __name__ == '__main__':
    if not TOKEN:
        logger.error("Lỗi: Chưa cấu hình TELEGRAM_BOT_TOKEN trong file .env")
        sys.exit(1)

    logger.info("🚀 Bot đang khởi động với dữ liệu OKX...")
    
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers
    start_handler = CommandHandler('start', start)
    crypto_handler = CommandHandler('crypto', get_crypto_prices)
    check_handler = CommandHandler('check', accuracy_check)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    
    application.add_handler(start_handler)
    application.add_handler(crypto_handler)
    application.add_handler(check_handler)
    application.add_handler(msg_handler)
    
    application.run_polling()
