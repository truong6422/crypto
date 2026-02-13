"""Core utility functions."""

import uuid
from typing import Any, Dict, Optional


def generate_uuid() -> str:
    """
    Tạo UUID string.
    
    Returns:
        str: UUID string
    """
    return str(uuid.uuid4())


def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Lấy giá trị từ dictionary một cách an toàn.
    
    Args:
        dictionary: Dictionary cần truy cập
        key: Key cần lấy
        default: Giá trị mặc định nếu key không tồn tại
        
    Returns:
        Any: Giá trị của key hoặc default
    """
    return dictionary.get(key, default)


def format_error_message(message: str, **kwargs) -> str:
    """
    Format error message với parameters.
    
    Args:
        message: Message template
        **kwargs: Parameters để format
        
    Returns:
        str: Formatted message
    """
    try:
        return message.format(**kwargs)
    except (KeyError, ValueError):
        return message


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> list:
    """
    Validate required fields trong data.
    
    Args:
        data: Data cần validate
        required_fields: List các field bắt buộc
        
    Returns:
        list: List các field bị thiếu
    """
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    return missing_fields 