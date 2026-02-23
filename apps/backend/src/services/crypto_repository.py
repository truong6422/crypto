"""Repository quản lý dữ liệu lịch sử Crypto."""
from sqlalchemy.orm import Session
from sqlalchemy import func, delete
from datetime import datetime, timedelta
from ..models import CryptoHistory, CryptoDaily
import logging
from .ta_service import TechnicalAnalysisService

logger = logging.getLogger(__name__)

class CryptoRepository:
    """Xử lý các thao tác database cho Crypto."""

    @staticmethod
    def save_price(db: Session, symbol: str, price: float, timeframe: str = "1m", timestamp: datetime = None):
        """Lưu giá mới vào lịch sử."""
        if timeframe == "1D":
            db_history = CryptoDaily(
                symbol=symbol, 
                price=price, 
                timestamp=timestamp if timestamp else datetime.utcnow()
            )
        else:
            db_history = CryptoHistory(
                symbol=symbol, 
                price=price, 
                timestamp=timestamp if timestamp else datetime.utcnow()
            )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    @staticmethod
    def get_last_price(db: Session, symbol: str, timeframe: str = "1m") -> float:
        """Lấy giá gần nhất trong database theo khung thời gian."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        last_record = db.query(model).filter(
            model.symbol == symbol
        ).order_by(model.timestamp.desc()).first()
        return float(last_record.price) if last_record else 0.0

    @staticmethod
    def get_average_price(db: Session, symbol: str, hours: int = 24, timeframe: str = "1m"):
        """Tính giá trung bình trong X giờ qua theo khung thời gian."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        since = datetime.utcnow() - timedelta(hours=hours)
        avg_price = db.query(func.avg(model.price)).filter(
            model.symbol == symbol,
            model.timestamp >= since
        ).scalar()
        return float(avg_price) if avg_price else 0

    @staticmethod
    def get_price_stats(db: Session, symbol: str, hours: int = 24, timeframe: str = "1m"):
        """Lấy giá cao nhất và thấp nhất trong X giờ qua."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        since = datetime.utcnow() - timedelta(hours=hours)
        stats = db.query(
            func.max(model.price).label("max_price"),
            func.min(model.price).label("min_price")
        ).filter(
            model.symbol == symbol,
            model.timestamp >= since
        ).first()
        return {
            "max": float(stats.max_price) if stats and stats.max_price else 0,
            "min": float(stats.min_price) if stats and stats.min_price else 0
        }

    @staticmethod
    def clear_old_data(db: Session, hours: int = 168, timeframe: str = "1m"):
        """Xóa dữ liệu cũ theo khung thời gian."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        threshold = datetime.utcnow() - timedelta(hours=hours)
        try:
            stmt = delete(model).where(
                model.timestamp < threshold
            )
            result = db.execute(stmt)
            db.commit()
            logger.info(f"Đã dọn dẹp {result.rowcount} bản ghi {timeframe} cũ.")
            return result.rowcount
        except Exception as e:
            db.rollback()
            logger.error(f"Lỗi khi dọn dẹp dữ liệu crypto ({timeframe}): {e}")
            return 0

    @staticmethod
    def get_recent_history(db: Session, symbol: str, limit: int = 100, timeframe: str = "1m"):
        """Lấy danh sách lịch sử giá gần nhất theo khung thời gian."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        records = db.query(model).filter(
            model.symbol == symbol
        ).order_by(model.timestamp.desc()).limit(limit).all()
        
        return [
            {"price": r.price, "timestamp": r.timestamp} 
            for r in reversed(records)
        ]
            
    @staticmethod
    def get_investment_suggestion(db: Session, symbol: str, current_price: float):
        """
        Đưa ra gợi ý đầu tư thông minh dựa trên RSI, MACD và Bollinger Bands (1m).
        Kết hợp xu hướng dài hạn (1D).
        """
        # 1. Tính toán TA ngắn hạn (1m)
        history_1m = CryptoRepository.get_recent_history(db, symbol, limit=100, timeframe="1m")
        ta_1m = TechnicalAnalysisService.calculate_indicators(history_1m)
        
        # 2. Lấy xu hướng dài hạn (1D)
        last_price_1d = CryptoRepository.get_last_price(db, symbol, timeframe="1D")
        trend_1d = ""
        if last_price_1d > 0:
            change_1d = ((current_price - last_price_1d) / last_price_1d) * 100
            trend_1d = f" | Ngày: {'📈' if change_1d > 0 else '📉'} {change_1d:+.1f}%"

        rsi = ta_1m.get("rsi")
        bb = ta_1m.get("bbands")
        macd = ta_1m.get("macd")

        # 3. Logic gợi ý đa chỉ số
        suggestion = "⚪ Trạng thái: THEO DÕI"
        
        if rsi and rsi < 30:
            if bb and current_price <= bb["lower"]:
                suggestion = "🔥 Gợi ý: MUA MẠNH (Đáy Bollinger)"
            else:
                suggestion = "🟢 Gợi ý: NÊN MUA (RSI thấp)"
        elif rsi and rsi > 70:
            if bb and current_price >= bb["upper"]:
                suggestion = "🔴 Gợi ý: NÊN CHỐT LỜI (Đỉnh Bollinger)"
            else:
                suggestion = "⚠️ Gợi ý: CẨN TRỌNG (RSI cao)"
        elif macd and macd["hist"]:
            if macd["hist"] > 0 and macd["value"] > macd["signal"]:
                suggestion = "📈 Xu hướng: TĂNG TRƯỞNG"
            elif macd["hist"] < 0 and macd["value"] < macd["signal"]:
                suggestion = "📉 Xu hướng: GIẢM GIÁ"

        ta_info = f" [RSI: {rsi:.1f}]" if rsi else ""
        return f"{suggestion}{ta_info}{trend_1d}"
