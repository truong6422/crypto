#!/usr/bin/env python3
"""Seed script cho các danh mục cơ bản."""

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Category


def seed_categories():
    """Seed các danh mục cơ bản."""
    
    # Danh sách các danh mục cơ bản
    categories_data = [
        # 1. Tỉnh thành phố
        {
            "name": "Hà Nội",
            "code": "HANOI",
            "value": "Hà Nội",
            "description": "Thành phố Hà Nội",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "TP. Hồ Chí Minh",
            "code": "HCM",
            "value": "TP. Hồ Chí Minh",
            "description": "Thành phố Hồ Chí Minh",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Đà Nẵng",
            "code": "DANANG",
            "value": "Đà Nẵng",
            "description": "Thành phố Đà Nẵng",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Hải Phòng",
            "code": "HAIPHONG",
            "value": "Hải Phòng",
            "description": "Thành phố Hải Phòng",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Cần Thơ",
            "code": "CANTHO",
            "value": "Cần Thơ",
            "description": "Thành phố Cần Thơ",
            "parent_id": None,
            "is_active": True
        },
        
        # 2. Dân tộc
        {
            "name": "Kinh",
            "code": "KINH",
            "value": "Kinh",
            "description": "Dân tộc Kinh",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Tày",
            "code": "TAY",
            "value": "Tày",
            "description": "Dân tộc Tày",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Thái",
            "code": "THAI",
            "value": "Thái",
            "description": "Dân tộc Thái",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Mường",
            "code": "MUONG",
            "value": "Mường",
            "description": "Dân tộc Mường",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Khmer",
            "code": "KHMER",
            "value": "Khmer",
            "description": "Dân tộc Khmer",
            "parent_id": None,
            "is_active": True
        },
        
        # 3. Bệnh tiền sử
        {
            "name": "Tiểu đường",
            "code": "DIABETES",
            "value": "Tiểu đường",
            "description": "Bệnh tiểu đường",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Cao huyết áp",
            "code": "HYPERTENSION",
            "value": "Cao huyết áp",
            "description": "Bệnh cao huyết áp",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Tim mạch",
            "code": "CARDIOVASCULAR",
            "value": "Tim mạch",
            "description": "Bệnh tim mạch",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Hen suyễn",
            "code": "ASTHMA",
            "value": "Hen suyễn",
            "description": "Bệnh hen suyễn",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Thận",
            "code": "KIDNEY",
            "value": "Thận",
            "description": "Bệnh thận",
            "parent_id": None,
            "is_active": True
        },
        
        # 4. ICD - Mã bệnh quốc tế
        {
            "name": "F20 - Tâm thần phân liệt",
            "code": "F20",
            "value": "Tâm thần phân liệt",
            "description": "ICD-10: F20 - Tâm thần phân liệt",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "F31 - Rối loạn cảm xúc lưỡng cực",
            "code": "F31",
            "value": "Rối loạn cảm xúc lưỡng cực",
            "description": "ICD-10: F31 - Rối loạn cảm xúc lưỡng cực",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "F32 - Trầm cảm",
            "code": "F32",
            "value": "Trầm cảm",
            "description": "ICD-10: F32 - Trầm cảm",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "F41 - Rối loạn lo âu",
            "code": "F41",
            "value": "Rối loạn lo âu",
            "description": "ICD-10: F41 - Rối loạn lo âu",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "F60 - Rối loạn nhân cách",
            "code": "F60",
            "value": "Rối loạn nhân cách",
            "description": "ICD-10: F60 - Rối loạn nhân cách",
            "parent_id": None,
            "is_active": True
        },
        
        # 5. Bệnh lý tâm thần
        {
            "name": "Tâm thần phân liệt",
            "code": "SCHIZOPHRENIA",
            "value": "Tâm thần phân liệt",
            "description": "Bệnh lý tâm thần phân liệt",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Trầm cảm",
            "code": "DEPRESSION",
            "value": "Trầm cảm",
            "description": "Bệnh lý trầm cảm",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Rối loạn lo âu",
            "code": "ANXIETY",
            "value": "Rối loạn lo âu",
            "description": "Bệnh lý rối loạn lo âu",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Rối loạn nhân cách",
            "code": "PERSONALITY_DISORDER",
            "value": "Rối loạn nhân cách",
            "description": "Bệnh lý rối loạn nhân cách",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Rối loạn ăn uống",
            "code": "EATING_DISORDER",
            "value": "Rối loạn ăn uống",
            "description": "Bệnh lý rối loạn ăn uống",
            "parent_id": None,
            "is_active": True
        },
        
        # 6. Chế độ chăm sóc
        {
            "name": "Chăm sóc đặc biệt",
            "code": "INTENSIVE_CARE",
            "value": "Chăm sóc đặc biệt",
            "description": "Chế độ chăm sóc đặc biệt",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Chăm sóc thường",
            "code": "GENERAL_CARE",
            "value": "Chăm sóc thường",
            "description": "Chế độ chăm sóc thường",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Chăm sóc tại nhà",
            "code": "HOME_CARE",
            "value": "Chăm sóc tại nhà",
            "description": "Chế độ chăm sóc tại nhà",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Chăm sóc ban ngày",
            "code": "DAY_CARE",
            "value": "Chăm sóc ban ngày",
            "description": "Chế độ chăm sóc ban ngày",
            "parent_id": None,
            "is_active": True
        },
        
        # 7. Chế độ dinh dưỡng
        {
            "name": "Chế độ ăn thường",
            "code": "NORMAL_DIET",
            "value": "Chế độ ăn thường",
            "description": "Chế độ dinh dưỡng thường",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Chế độ ăn kiêng muối",
            "code": "LOW_SALT_DIET",
            "value": "Chế độ ăn kiêng muối",
            "description": "Chế độ dinh dưỡng kiêng muối",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Chế độ ăn kiêng đường",
            "code": "LOW_SUGAR_DIET",
            "value": "Chế độ ăn kiêng đường",
            "description": "Chế độ dinh dưỡng kiêng đường",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Chế độ ăn mềm",
            "code": "SOFT_DIET",
            "value": "Chế độ ăn mềm",
            "description": "Chế độ dinh dưỡng mềm",
            "parent_id": None,
            "is_active": True
        },
        
        # 8. Đánh giá, phân loại đối tượng
        {
            "name": "Không có nguy cơ",
            "code": "NO_RISK",
            "value": "Không có nguy cơ",
            "description": "Đánh giá không có nguy cơ",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Nguy cơ thấp",
            "code": "LOW_RISK",
            "value": "Nguy cơ thấp",
            "description": "Đánh giá nguy cơ thấp",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Nguy cơ trung bình",
            "code": "MEDIUM_RISK",
            "value": "Nguy cơ trung bình",
            "description": "Đánh giá nguy cơ trung bình",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Nguy cơ cao",
            "code": "HIGH_RISK",
            "value": "Nguy cơ cao",
            "description": "Đánh giá nguy cơ cao",
            "parent_id": None,
            "is_active": True
        },
        
        # 9. Thuốc
        {
            "name": "Olanzapine",
            "code": "OLANZAPINE",
            "value": "Olanzapine",
            "description": "Thuốc chống loạn thần",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Risperidone",
            "code": "RISPERIDONE",
            "value": "Risperidone",
            "description": "Thuốc chống loạn thần",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Fluoxetine",
            "code": "FLUOXETINE",
            "value": "Fluoxetine",
            "description": "Thuốc chống trầm cảm",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Diazepam",
            "code": "DIAZEPAM",
            "value": "Diazepam",
            "description": "Thuốc an thần",
            "parent_id": None,
            "is_active": True
        },
        
        # 10. Vật tư y tế
        {
            "name": "Băng gạc",
            "code": "BANDAGE",
            "value": "Băng gạc",
            "description": "Vật tư y tế - Băng gạc",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Kim tiêm",
            "code": "SYRINGE",
            "value": "Kim tiêm",
            "description": "Vật tư y tế - Kim tiêm",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Găng tay",
            "code": "GLOVES",
            "value": "Găng tay",
            "description": "Vật tư y tế - Găng tay",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Khẩu trang",
            "code": "MASK",
            "value": "Khẩu trang",
            "description": "Vật tư y tế - Khẩu trang",
            "parent_id": None,
            "is_active": True
        },
        
        # 11. Phòng ban
        {
            "name": "Khoa Tâm thần",
            "code": "PSYCHIATRY",
            "value": "Khoa Tâm thần",
            "description": "Phòng ban - Khoa Tâm thần",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Khoa Nội",
            "code": "INTERNAL_MEDICINE",
            "value": "Khoa Nội",
            "description": "Phòng ban - Khoa Nội",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Khoa Ngoại",
            "code": "SURGERY",
            "value": "Khoa Ngoại",
            "description": "Phòng ban - Khoa Ngoại",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Phòng Khám",
            "code": "CLINIC",
            "value": "Phòng Khám",
            "description": "Phòng ban - Phòng Khám",
            "parent_id": None,
            "is_active": True
        },
        
        # 12. Các tổ
        {
            "name": "Tổ Điều dưỡng",
            "code": "NURSING_TEAM",
            "value": "Tổ Điều dưỡng",
            "description": "Tổ - Tổ Điều dưỡng",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Tổ Bác sĩ",
            "code": "DOCTOR_TEAM",
            "value": "Tổ Bác sĩ",
            "description": "Tổ - Tổ Bác sĩ",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Tổ Hành chính",
            "code": "ADMIN_TEAM",
            "value": "Tổ Hành chính",
            "description": "Tổ - Tổ Hành chính",
            "parent_id": None,
            "is_active": True
        },
        {
            "name": "Tổ Kỹ thuật",
            "code": "TECHNICAL_TEAM",
            "value": "Tổ Kỹ thuật",
            "description": "Tổ - Tổ Kỹ thuật",
            "parent_id": None,
            "is_active": True
        }
    ]
    
    db = next(get_db())
    
    try:
        # Kiểm tra xem đã có dữ liệu chưa
        existing_count = db.query(Category).count()
        if existing_count > 0:
            print(f"Đã có {existing_count} danh mục trong database. Bỏ qua seeding.")
            return
        
        # Tạo các danh mục
        for category_data in categories_data:
            category = Category(
                name=category_data["name"],
                code=category_data["code"],
                value=category_data["value"],
                description=category_data["description"],
                parent_id=category_data["parent_id"],
                is_active=category_data["is_active"],
                created_by="system"
            )
            db.add(category)
        
        db.commit()
        print(f"Đã tạo thành công {len(categories_data)} danh mục cơ bản.")
        
    except Exception as e:
        db.rollback()
        print(f"Lỗi khi tạo danh mục: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Bắt đầu seeding categories...")
    seed_categories()
    print("Hoàn thành seeding categories.") 