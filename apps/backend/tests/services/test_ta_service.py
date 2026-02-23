import pytest
from src.services.ta_service import TechnicalAnalysisService
from datetime import datetime, timedelta

def test_calculate_indicators_insufficient_data():
    """Kiểm tra trường hợp dữ liệu không đủ."""
    data = [{"price": 100, "timestamp": datetime.now()}] * 5
    result = TechnicalAnalysisService.calculate_indicators(data)
    assert result["status"] == "Dữ liệu không đủ (Cần ít nhất 20 điểm dữ liệu)"
    assert result["rsi"] is None

def test_calculate_indicators_success():
    """Kiểm tra tính toán thành công với dữ liệu giả lập."""
    # Tạo 100 điểm dữ liệu giá tăng dần
    data = []
    base_time = datetime.now()
    for i in range(100):
        data.append({
            "price": 100 + i, 
            "timestamp": base_time + timedelta(minutes=i)
        })
    
    result = TechnicalAnalysisService.calculate_indicators(data)
    assert result["status"] == "success"
    assert result["rsi"] is not None
    assert 0 <= result["rsi"] <= 100
    assert result["bbands"]["upper"] > result["bbands"]["lower"]
    assert "macd" in result
