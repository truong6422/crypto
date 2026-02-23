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
    def save_price(db: Session, symbol: str, price: float, timeframe: str = "1m", timestamp: datetime = None, 
                   open_p: float = None, high: float = None, low: float = None, volume: float = None):
        """Lưu nến mới vào lịch sử."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        
        db_history = model(
            symbol=symbol, 
            open=open_p if open_p else price,
            high=high if high else price,
            low=low if low else price,
            close=price,
            volume=volume if volume else 0,
            timestamp=timestamp if timestamp else datetime.utcnow()
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)
        return db_history

    @staticmethod
    def get_last_price(db: Session, symbol: str, timeframe: str = "1m") -> float:
        """Lấy giá gần nhất."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        last_record = db.query(model).filter(
            model.symbol == symbol
        ).order_by(model.timestamp.desc()).first()
        return float(last_record.close) if last_record else 0.0

    @staticmethod
    def get_average_price(db: Session, symbol: str, hours: int = 24, timeframe: str = "1m"):
        """Tính giá trung bình."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        since = datetime.utcnow() - timedelta(hours=hours)
        avg_price = db.query(func.avg(model.close)).filter(
            model.symbol == symbol,
            model.timestamp >= since
        ).scalar()
        return float(avg_price) if avg_price else 0

    @staticmethod
    def get_price_stats(db: Session, symbol: str, hours: int = 24, timeframe: str = "1m"):
        """Lấy giá cao nhất và thấp nhất."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        since = datetime.utcnow() - timedelta(hours=hours)
        stats = db.query(
            func.max(model.high).label("max_price"),
            func.min(model.low).label("min_price")
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
        """Lấy danh sách nến (OHLCV) gần nhất."""
        model = CryptoDaily if timeframe == "1D" else CryptoHistory
        records = db.query(model).filter(
            model.symbol == symbol
        ).order_by(model.timestamp.desc()).limit(limit).all()
        
        return [
            {
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume,
                "timestamp": r.timestamp
            } 
            for r in reversed(records)
        ]
            
    @staticmethod
    def get_investment_suggestion(db: Session, symbol: str, current_price: float):
        """
        Đưa ra gợi ý dựa trên Signal Scoring System (Điểm số tín hiệu).
        """
        # 1. Lấy dữ liệu 1m và 1D
        history_1m = CryptoRepository.get_recent_history(db, symbol, limit=100, timeframe="1m")
        history_1d = CryptoRepository.get_recent_history(db, symbol, limit=30, timeframe="1D")
        
        # 2. Kiểm tra dữ liệu đủ để phân tích chưa
        if ta_1m.get("status") != "success":
            return f"⚪ ĐANG CẬP NHẬT [Chưa đủ dữ liệu nến]"

        score = 0
        reasons = []

        # --- Tín hiệu RSI (1m) ---
        rsi_1m = ta_1m.get("rsi")
        if rsi_1m is not None:
            if rsi_1m < 30:
                score += 2
                reasons.append(f"RSI Quá bán ({rsi_1m:.1f})")
            elif rsi_1m < 40:
                score += 1
                reasons.append("RSI Thấp")
            elif rsi_1m > 70:
                score -= 2
                reasons.append(f"RSI Quá mua ({rsi_1m:.1f})")
            elif rsi_1m > 60:
                score -= 1
                reasons.append("RSI Cao")

        # --- Tín hiệu Bollinger Bands (1m) ---
        bb = ta_1m.get("bbands")
        if bb and bb["lower"] is not None and bb["upper"] is not None:
            if current_price <= bb["lower"]:
                score += 2
                reasons.append("Chạm đáy BB")
            elif current_price >= bb["upper"]:
                score -= 2
                reasons.append("Chạm đỉnh BB")

        # --- Xu hướng nến ngày (1D) ---
        rsi_1d = ta_1d.get("rsi")
        if rsi_1d is not None:
            if rsi_1d > 55:
                score += 1
                reasons.append("Xu hướng ngày Tăng")
            elif rsi_1d < 45:
                score -= 1
                reasons.append("Xu hướng ngày Giảm")

        # --- Kết luận dựa trên điểm ---
        status = "⚪ TRUNG LẬP"
        if score >= 4:
            status = "🔥 MUA MẠNH"
        elif score >= 2:
            status = "🟢 MUA"
        elif score <= -4:
            status = "💀 BÁN MẠNH"
        elif score <= -2:
            status = "🔴 BÁN"

        reasons_text = f" | {', '.join(reasons[:2])}" if reasons else ""
        return f"<b>{status}</b> [Điểm: {score:+} {reasons_text}]"
