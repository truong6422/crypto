"""Dịch vụ tính toán các chỉ số kỹ thuật (Technical Analysis)."""
import pandas as pd
import pandas_ta as ta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    """Xử lý các tính toán kỹ thuật RSI, MACD, Bollinger Bands dùng pandas-ta."""

    @staticmethod
    def calculate_indicators(history_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Tính toán các chỉ số kỹ thuật từ dữ liệu lịch sử.
        
        Args:
            history_data: Danh sách các bản ghi từ database (symbol, price, timestamp).
            
        Returns:
            Dict chứa các giá trị chỉ số mới nhất (RSI, MACD, BBands).
        """
        if not history_data or len(history_data) < 20:
            return {
                "rsi": None,
                "macd": None,
                "bbands": None,
                "status": "Dữ liệu không đủ (Cần ít nhất 20 điểm dữ liệu)"
            }

        try:
            # 1. Chuyển đổi sang DataFrame
            df = pd.DataFrame(history_data)
            if 'close' not in df.columns and 'price' in df.columns:
                df['close'] = df['price'].astype(float)
            
            df['close'] = df['close'].astype(float)
            df = df.sort_values('timestamp')

            # 2. Tính toán RSI (chu kỳ 14)
            df.ta.rsi(length=14, append=True)
            
            # 3. Tính toán MACD (12, 26, signal 9)
            df.ta.macd(fast=12, slow=26, signal=9, append=True)
            
            # 4. Tính toán Bollinger Bands (20, 2)
            df.ta.bbands(length=20, std=2, append=True)

            # 5. Lấy kết quả mới nhất
            latest = df.iloc[-1]
            
            # Tìm tên cột RSI (thường là RSI_14)
            rsi_col = [c for c in df.columns if c.startswith('RSI_')]
            rsi_val = float(latest[rsi_col[0]]) if rsi_col and not pd.isna(latest[rsi_col[0]]) else None

            # Tìm các cột MACD
            macd_val = None
            macd_signal = None
            macd_hist = None
            macd_cols = [c for c in df.columns if c.startswith('MACD_')]
            macd_s_cols = [c for c in df.columns if c.startswith('MACDs_')]
            macd_h_cols = [c for c in df.columns if c.startswith('MACDh_')]
            
            if macd_cols: macd_val = float(latest[macd_cols[0]]) if not pd.isna(latest[macd_cols[0]]) else None
            if macd_s_cols: macd_signal = float(latest[macd_s_cols[0]]) if not pd.isna(latest[macd_s_cols[0]]) else None
            if macd_h_cols: macd_hist = float(latest[macd_h_cols[0]]) if not pd.isna(latest[macd_h_cols[0]]) else None

            # Tìm các cột Bollinger Bands
            bb_upper = None
            bb_middle = None
            bb_lower = None
            bbu_cols = [c for c in df.columns if c.startswith('BBU_')]
            bbm_cols = [c for c in df.columns if c.startswith('BBM_')]
            bbl_cols = [c for c in df.columns if c.startswith('BBL_')]

            if bbu_cols: bb_upper = float(latest[bbu_cols[0]]) if not pd.isna(latest[bbu_cols[0]]) else None
            if bbm_cols: bb_middle = float(latest[bbm_cols[0]]) if not pd.isna(latest[bbm_cols[0]]) else None
            if bbl_cols: bb_lower = float(latest[bbl_cols[0]]) if not pd.isna(latest[bbl_cols[0]]) else None

            result = {
                "rsi": rsi_val,
                "macd": {
                    "value": macd_val,
                    "signal": macd_signal,
                    "hist": macd_hist,
                },
                "bbands": {
                    "upper": bb_upper,
                    "middle": bb_middle,
                    "lower": bb_lower,
                },
                "status": "success"
            }
            
            return result

        except Exception as e:
            logger.error(f"Lỗi khi tính toán chỉ số TA: {e}")
            return {
                "rsi": None,
                "macd": None,
                "bbands": None,
                "status": f"Lỗi tính toán: {str(e)}"
            }
