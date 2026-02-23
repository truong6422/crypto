"""Service crawl thông tin từ sàn OKX."""
import requests
import logging
from typing import Dict, Any, List, Optional
from ..config import settings
from ..constants import CryptoAssets

logger = logging.getLogger(__name__)

class CryptoScraperService:
    """Service hỗ trợ lấy thông tin giá crypto từ OKX V5 API."""
    
    BASE_URL = "https://www.okx.com/api/v5"
    
    @classmethod
    def get_prices(cls, ids: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Lấy thông tin giá crypto từ OKX.
        
        Returns:
            List[Dict]: Danh sách thông tin giá từ OKX.
        """
        url = f"{cls.BASE_URL}/market/tickers"
        params = {"instType": "SPOT"}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            all_tickers = response.json().get("data", [])
            
            target_ids = ids or CryptoAssets.DEFAULT_IDS
            # Lọc chỉ lấy những mã chúng ta quan tâm
            filtered_data = [t for t in all_tickers if t.get("instId") in target_ids]
            return filtered_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Lỗi khi crawl dữ liệu từ OKX: {e}")
            return []

    @classmethod
    def format_price_message(cls, data: List[Dict[str, Any]]) -> str:
        """ Định dạng dữ liệu từ OKX thành tin nhắn văn bản. """
        if not data:
            return "❌ Không thể lấy dữ liệu từ OKX lúc này."
            
        message = "<b>📊 GIÁ CRYPTO REAL-TIME (OKX)</b>\n"
        message += "----------------------------------\n\n"
        
        for coin in data:
            inst_id = coin.get("instId", "Unknown")
            last_price = float(coin.get("last", 0))
            open_24h = float(coin.get("open24h", 0))
            high_24h = float(coin.get("high24h", 0))
            low_24h = float(coin.get("low24h", 0))
            
            # Tính % thay đổi
            change_pct = ((last_price - open_24h) / open_24h * 100) if open_24h > 0 else 0
            trend = "🟢" if change_pct >= 0 else "🔴"
            
            message += f"<b>🔸 {inst_id}</b> {trend}\n"
            message += f"💰 Giá: <b>${last_price:,.2f}</b> ({change_pct:+.2f}%)\n"
            message += f"📈 Cao nhất: ${high_24h:,.2f}\n"
            message += f"📉 Thấp nhất: ${low_24h:,.2f}\n"
            message += "\n"
            
        message += "<i>Nguồn: OKX Exchange</i>"
        return message
