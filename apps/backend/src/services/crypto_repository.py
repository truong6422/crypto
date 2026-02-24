"""Repository quản lý dữ liệu lịch sử Crypto."""
from sqlalchemy.orm import Session
from sqlalchemy import func, delete
from datetime import datetime, timedelta
from ..models import CryptoHistory, CryptoDaily, TradingSignal
from ..constants import CryptoConfig
import logging
from .ta_service import TechnicalAnalysisService

logger = logging.getLogger(__name__)

class CryptoRepository:
    """Xử lý các thao tác database cho Crypto."""

    @staticmethod
    def record_signal(db: Session, symbol: str, signal_type: str, score: int, entry_price: float):
        """Lưu một tín hiệu mới để theo dõi hiệu quả (Bỏ cooldown để test)."""
        try:
            new_signal = TradingSignal(
                symbol=symbol,
                signal_type=signal_type,
                score=score,
                entry_price=entry_price,
                status="PENDING",
                timestamp=datetime.utcnow()
            )
            db.add(new_signal)
            db.commit()
            db.refresh(new_signal)
            logger.info(f"✅ Đã ghi nhận tín hiệu {signal_type} cho {symbol} tại giá {entry_price}")
            return new_signal
        except Exception as e:
            db.rollback()
            logger.error(f"❌ Lỗi khi lưu TradingSignal: {e}")
            return None

    @staticmethod
    def validate_signals(db: Session):
        """Kiểm tra kết quả các tín hiệu sau 1 giờ."""
        from .crypto_scraper import CryptoScraperService
        
        # Lấy các tín hiệu PENDING đã đủ thời gian chờ (ít nhất 1 phút) để giá kịp biến động
        threshold = datetime.utcnow() - timedelta(minutes=CryptoConfig.SIGNAL_VALIDATE_THRESHOLD_MINUTES)
        pending_signals = db.query(TradingSignal).filter(
            TradingSignal.status == "PENDING",
            TradingSignal.timestamp <= threshold
        ).all()

        if not pending_signals:
            return 0

        # Lấy giá hiện tại từ OKX
        current_data = CryptoScraperService.get_prices()
        price_map = {item["instId"]: float(item["last"]) for item in current_data}

        count = 0
        for signal in pending_signals:
            curr_price = price_map.get(signal.symbol)
            if not curr_price:
                continue
            
            signal.exit_price = curr_price
            signal.status = "COMPLETED"
            signal.closed_at = datetime.utcnow()
            
            # Tính toán kết quả
            if signal.signal_type == "BUY":
                signal.result = "WIN" if curr_price > signal.entry_price else "LOSS"
            else: # SELL
                signal.result = "WIN" if curr_price < signal.entry_price else "LOSS"
            
            count += 1
        
        db.commit()
        return count

    @staticmethod
    def get_accuracy_report(db: Session):
        """Lấy báo cáo tỷ lệ chính xác."""
        total = db.query(TradingSignal).filter(TradingSignal.status == "COMPLETED").count()
        if total == 0:
            return "Chưa có đủ dữ liệu đối soát tín hiệu."
        
        wins = db.query(TradingSignal).filter(
            TradingSignal.status == "COMPLETED",
            TradingSignal.result == "WIN"
        ).count()
        
        win_rate = (wins / total) * 100
        
        # Thống kê theo tuần
        week_ago = datetime.utcnow() - timedelta(days=7)
        total_7d = db.query(TradingSignal).filter(
            TradingSignal.status == "COMPLETED",
            TradingSignal.timestamp >= week_ago
        ).count()
        
        wins_7d = db.query(TradingSignal).filter(
            TradingSignal.status == "COMPLETED",
            TradingSignal.result == "WIN",
            TradingSignal.timestamp >= week_ago
        ).count()
        
        win_rate_7d = (wins_7d / total_7d * 100) if total_7d > 0 else 0

        report = (
            f"📊 <b>THỐNG KÊ ĐỘ CHÍNH XÁC</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🏆 Tổng Win Rate: <b>{win_rate:.1f}%</b>\n"
            f"📈 Tổng số kèo: {total} ({wins} Thắng)\n\n"
            f"📅 Trong 7 ngày qua:\n"
            f"┗ Win Rate: <b>{win_rate_7d:.1f}%</b>\n"
            f"┗ Số kèo: {total_7d}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        return report

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
        
        ta_1m = TechnicalAnalysisService.calculate_indicators(history_1m)
        ta_1d = TechnicalAnalysisService.calculate_indicators(history_1d)

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
        signal_type = None

        if score >= 4:
            status = "🔥 MUA MẠNH"
            signal_type = "BUY"
        elif score >= 2:
            status = "🟢 MUA"
            signal_type = "BUY"
        elif score <= -4:
            status = "💀 BÁN MẠNH"
            signal_type = "SELL"
        elif score <= -2:
            status = "🔴 BÁN"
            signal_type = "SELL"

        if signal_type:
            CryptoRepository.record_signal(db, symbol, signal_type, score, current_price)

        reasons_text = f" | {', '.join(reasons[:2])}" if reasons else ""
        return f"<b>{status}</b> [Điểm: {score:+} {reasons_text}]"
