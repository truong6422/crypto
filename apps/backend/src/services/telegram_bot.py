"""Service gửi thông báo qua Telegram."""
import requests
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

class TelegramService:
    """Service hỗ trợ gửi tin nhắn telegram."""
    
    @staticmethod
    def send_message(message: str, chat_id: Optional[str] = None) -> bool:
        """
        Gửi tin nhắn đến Telegram chat.
        
        Args:
            message: Nội dung tin nhắn.
            chat_id: ID chat nhận tin nhắn (mặc định lấy từ settings).
            
        Returns:
            bool: True nếu gửi thành công, ngược lại False.
        """
        token = settings.TELEGRAM_BOT_TOKEN
        target_chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        
        if not token or not target_chat_id:
            logger.error("Telegram token hoặc chat_id chưa được cấu hình.")
            return False
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": target_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi gửi tin nhắn Telegram: {e}")
            return False
