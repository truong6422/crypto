"""Repository quản lý dữ liệu lịch sử Crypto."""
from sqlalchemy.orm import Session
from sqlalchemy import func, delete
from datetime import datetime, timedelta
from ..models import CryptoHistory
import logging

logger = logging.getLogger(__name__)

class CryptoRepository:
    """Xử lý các thao tác database cho Crypto."""

    @staticmethod
    def save_price(db: Session, symbol: str, price: float):
        """Lưu giá mới vào lịch sử."""
        db_history = CryptoHistory(symbol=symbol, price=price)
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    @staticmethod
    def get_last_price(db: Session, symbol: str) -> float:
        """Lấy giá gần nhất trong database."""
        last_record = db.query(CryptoHistory).filter(
            CryptoHistory.symbol == symbol
        ).order_by(CryptoHistory.timestamp.desc()).first()
        return float(last_record.price) if last_record else 0.0

    @staticmethod
    def get_average_price(db: Session, symbol: str, hours: int = 24):
        """Tính giá trung bình trong X giờ qua."""
        since = datetime.utcnow() - timedelta(hours=hours)
        avg_price = db.query(func.avg(CryptoHistory.price)).filter(
            CryptoHistory.symbol == symbol,
            CryptoHistory.timestamp >= since
        ).scalar()
        return float(avg_price) if avg_price else 0

    @staticmethod
    def get_price_stats(db: Session, symbol: str, hours: int = 24):
        """Lấy giá cao nhất và thấp nhất trong X giờ qua."""
        since = datetime.utcnow() - timedelta(hours=hours)
        stats = db.query(
            func.max(CryptoHistory.price).label("max_price"),
            func.min(CryptoHistory.price).label("min_price")
        ).filter(
            CryptoHistory.symbol == symbol,
            CryptoHistory.timestamp >= since
        ).first()
        return {
            "max": float(stats.max_price) if stats and stats.max_price else 0,
            "min": float(stats.min_price) if stats and stats.min_price else 0
        }

    @staticmethod
    def clear_old_data(db: Session, hours: int = 168): # Mặc định 1 tuần (168h)
        """Xóa dữ liệu cũ để tránh tràn bộ nhớ."""
        threshold = datetime.utcnow() - timedelta(hours=hours)
        try:
            stmt = delete(CryptoHistory).where(CryptoHistory.timestamp < threshold)
            result = db.execute(stmt)
            db.commit()
            logger.info(f"Đã dọn dẹp {result.rowcount} bản ghi crypto cũ.")
            return result.rowcount
        except Exception as e:
            db.rollback()
            logger.error(f"Lỗi khi dọn dẹp dữ liệu crypto: {e}")
            return 0
            
    @staticmethod
    def get_investment_suggestion(db: Session, symbol: str, current_price: float):
        """
        Đưa ra gợi ý đầu tư thông minh dựa trên:
        1. Trung bình động (SMA) 1h, 4h, 24h.
        2. Vị thế giá so với biên độ 24h (Overbought/Oversold).
        """
        avg_1h = CryptoRepository.get_average_price(db, symbol, hours=1)
        avg_4h = CryptoRepository.get_average_price(db, symbol, hours=4)
        avg_24h = CryptoRepository.get_average_price(db, symbol, hours=24)
        stats_24h = CryptoRepository.get_price_stats(db, symbol, hours=24)
        
        if avg_1h == 0 or avg_24h == 0:
            return "⏳ Đang thu thập dữ liệu..."
            
        # 1. Tính toán các chỉ số
        diff_1h = ((current_price - avg_1h) / avg_1h) * 100
        # Vị thế trong biên độ 24h (0% là đáy, 100% là đỉnh)
        range_24h = stats_24h["max"] - stats_24h["min"]
        position_pct = ((current_price - stats_24h["min"]) / range_24h * 100) if range_24h > 0 else 50

        # 2. Logic gợi ý
        # TRƯỜNG HỢP MUA: Giá thấp hơn trung bình 1h và đang ở vùng đáy 24h
        if diff_1h < -0.5 and position_pct < 30:
            return "🔥 Gợi ý: MUA MẠNH (Vùng đáy 24h & Giá chiết khấu)"
        elif diff_1h < -1:
            return "🟢 Gợi ý: NÊN MUA (Giá đang điều chỉnh ngắn hạn)"
            
        # TRƯỜNG HỢP BÁN/ĐỢI: Giá cao hơn trung bình 1h và đang ở vùng đỉnh 24h
        if diff_1h > 0.5 and position_pct > 80:
            return "🔴 Gợi ý: NÊN CHỐT LỜI (Vùng đỉnh 24h, rủi ro cao)"
        elif diff_1h > 1.5:
            return "⚠️ Gợi ý: CẨN TRỌNG (Giá đang tăng nóng)"
            
        # XU HƯỚNG
        if avg_1h > avg_4h > avg_24h:
            return "📈 Xu hướng: TĂNG TRƯỞNG (Có thể giữ thêm)"
        elif avg_1h < avg_4h < avg_24h:
            return "📉 Xu hướng: GIẢM GIÁ (Nên quan sát thêm)"
            
        return "⚪ Trạng thái: THEO DÕI (Thị trường đi ngang)"
