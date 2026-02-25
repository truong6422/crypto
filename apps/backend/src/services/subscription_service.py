"""Service quản lý đăng ký thông báo của người dùng."""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models import UserSubscription

logger = logging.getLogger(__name__)

class SubscriptionService:
    @staticmethod
    def subscribe(db: Session, chat_id: str, symbol: str) -> UserSubscription:
        """Đăng ký nhận thông báo cho một mã coin."""
        # Chuẩn hóa symbol
        if not symbol.endswith("-USDT") and "-" not in symbol:
            symbol = f"{symbol.upper()}-USDT"
        
        # Kiểm tra xem đã đăng ký chưa
        existing = db.query(UserSubscription).filter(
            UserSubscription.chat_id == chat_id,
            UserSubscription.symbol == symbol
        ).first()
        
        if existing:
            existing.is_active = True
            db.commit()
            return existing
            
        new_sub = UserSubscription(chat_id=chat_id, symbol=symbol)
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)
        return new_sub

    @staticmethod
    def unsubscribe(db: Session, chat_id: str, symbol: str) -> bool:
        """Hủy đăng ký nhận thông báo."""
        if not symbol.endswith("-USDT") and "-" not in symbol:
            symbol = f"{symbol.upper()}-USDT"
            
        sub = db.query(UserSubscription).filter(
            UserSubscription.chat_id == chat_id,
            UserSubscription.symbol == symbol
        ).first()
        
        if sub:
            db.delete(sub)
            db.commit()
            return True
        return False

    @staticmethod
    def get_user_subscriptions(db: Session, chat_id: str) -> List[UserSubscription]:
        """Lấy danh sách các mã đã đăng ký của người dùng."""
        return db.query(UserSubscription).filter(
            UserSubscription.chat_id == chat_id,
            UserSubscription.is_active == True
        ).all()

    @staticmethod
    def get_all_subscribed_symbols(db: Session) -> List[str]:
        """Lấy danh sách tất cả các mã đang được ít nhất 1 người đăng ký."""
        results = db.query(UserSubscription.symbol).filter(
            UserSubscription.is_active == True
        ).distinct().all()
        return [r[0] for r in results]
