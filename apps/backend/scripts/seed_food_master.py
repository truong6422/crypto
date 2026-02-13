import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.meal_planning.models import FoodMaster
from src.models import Base

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/meal")

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

print(f"Using database URL: {db_url}")

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

print("🌱 Starting to seed food master data...")

food_data = [
    {"name": "Gạo nếp cái", "calories": 344.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Gạo tẻ giã", "calories": 344.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Gạo lứt", "calories": 345.0, "unit": "100g", "category": "Tinh bột"},
    {
        "name": "Bánh bao nhân thịt",
        "calories": 219.0,
        "unit": "100g",
        "category": "Tinh bột",
    },
    {"name": "Bánh mì", "calories": 249.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Bánh phở", "calories": 143.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Bánh quẩy", "calories": 292.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Bún", "calories": 110.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Mì sợi", "calories": 349.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Bắp nếp luộc", "calories": 167.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Cốm", "calories": 297.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Bột mì", "calories": 346.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Bắp rang", "calories": 372.0, "unit": "100g", "category": "Tinh bột"},
    {"name": "Miến dong", "calories": 332.0, "unit": "100g", "category": "Tinh bột"},
    {
        "name": "Thịt bò loại 1",
        "calories": 118.0,
        "unit": "100g",
        "category": "Chất đạm",
    },
    {"name": "Thịt cừu nạc", "calories": 219.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Thịt dê nạc", "calories": 122.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Thịt gà ta", "calories": 199.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Thịt heo mỡ", "calories": 394.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Thịt heo nạc", "calories": 139.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Thịt vịt", "calories": 267.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Chân giò heo", "calories": 230.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Chả lụa", "calories": 136.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Lạp xưởng", "calories": 585.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Chà bông heo", "calories": 369.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Thịt đùi ếch", "calories": 90.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Cá chép", "calories": 96.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Cá hồi", "calories": 136.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Cá ngừ", "calories": 87.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Cá thu", "calories": 166.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Cua biển", "calories": 103.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Cua đồng", "calories": 87.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Ghẹ", "calories": 54.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Mực tươi", "calories": 73.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Ốc bươu", "calories": 84.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Tôm biển", "calories": 82.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Tôm đồng", "calories": 90.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Trứng gà", "calories": 166.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Trứng vịt", "calories": 184.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Trứng cút", "calories": 154.0, "unit": "100g", "category": "Chất đạm"},
    {"name": "Trứng cá", "calories": 171.0, "unit": "100g", "category": "Chất đạm"},
    {
        "name": "Đậu cô ve",
        "calories": 73.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {
        "name": "Đậu đen",
        "calories": 325.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {
        "name": "Đậu đũa",
        "calories": 59.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {
        "name": "Đậu Hà Lan",
        "calories": 72.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {
        "name": "Đậu nành",
        "calories": 400.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {"name": "Sữa đậu nành", "calories": 28.0, "unit": "100g", "category": "Đồ uống"},
    {
        "name": "Đậu xanh",
        "calories": 328.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {
        "name": "Hạt điều khô chiên dầu",
        "calories": 583.0,
        "unit": "100g",
        "category": "Hạt",
    },
    {"name": "Mè đen", "calories": 568.0, "unit": "100g", "category": "Hạt"},
    {"name": "Mè trắng", "calories": 568.0, "unit": "100g", "category": "Hạt"},
    {
        "name": "Đậu phụ",
        "calories": 95.0,
        "unit": "100g",
        "category": "Chất đạm thực vật",
    },
    {"name": "Hạt bí rang", "calories": 519.0, "unit": "100g", "category": "Hạt"},
    {"name": "Hạt dưa rang", "calories": 551.0, "unit": "100g", "category": "Hạt"},
    {"name": "Nấm hương khô", "calories": 274.0, "unit": "100g", "category": "Nấm"},
    {"name": "Nấm mèo (mộc nhĩ)", "calories": 304.0, "unit": "100g", "category": "Nấm"},
    {"name": "Khoai lang", "calories": 119.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Khoai tây", "calories": 93.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Bầu", "calories": 14.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Bí xanh", "calories": 12.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Bí đỏ", "calories": 27.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Cà chua", "calories": 20.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Cà rốt", "calories": 39.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Cải bắp", "calories": 29.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Cải thìa", "calories": 17.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Cải xanh", "calories": 16.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Rau mồng tơi", "calories": 14.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Rau muống", "calories": 25.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Rau ngót", "calories": 35.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Củ cải trắng", "calories": 21.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Dưa chuột", "calories": 16.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Hạt sen tươi", "calories": 161.0, "unit": "100g", "category": "Hạt"},
    {"name": "Măng tây", "calories": 14.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Mướp", "calories": 17.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Khổ qua", "calories": 16.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Súp lơ xanh", "calories": 26.0, "unit": "100g", "category": "Rau củ"},
    {"name": "Bưởi", "calories": 30.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Cam", "calories": 38.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Chanh", "calories": 24.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Chôm chôm", "calories": 72.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Chuối tiêu", "calories": 97.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Dâu tây", "calories": 43.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Dưa hấu", "calories": 16.0, "unit": "100g", "category": "Trái cây"},
    {
        "name": "Dứa (thơm) tây",
        "calories": 38.0,
        "unit": "100g",
        "category": "Trái cây",
    },
    {"name": "Đào", "calories": 31.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Đu đủ chín", "calories": 35.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Lê", "calories": 45.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Lựu", "calories": 70.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Mận", "calories": 20.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Mít mật", "calories": 62.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Nhãn", "calories": 48.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Ổi", "calories": 38.0, "unit": "100g", "category": "Trái cây"},
    {"name": "Bia", "calories": 11.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Rượu nếp", "calories": 167.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Rượu vang đỏ", "calories": 9.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Coca cola", "calories": 42.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Nước cam tươi", "calories": 23.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Sữa bò tươi", "calories": 74.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Sữa chua", "calories": 61.0, "unit": "100g", "category": "Đồ uống"},
    {"name": "Kẹo cà phê", "calories": 378.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Kẹo dừa mềm", "calories": 415.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Kẹo sữa", "calories": 390.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Bánh socola", "calories": 449.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Bánh quế", "calories": 435.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Bánh đậu xanh", "calories": 416.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Bánh quy", "calories": 376.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Mứt cam có vỏ", "calories": 218.0, "unit": "100g", "category": "Đồ ngọt"},
    {"name": "Mứt thơm", "calories": 208.0, "unit": "100g", "category": "Đồ ngọt"},
]

for item in food_data:
    existing_food = (
        session.query(FoodMaster).filter(FoodMaster.name == item["name"]).first()
    )
    if existing_food:
        existing_food.calories = item["calories"]
        existing_food.category = item["category"]
        print(f"   🔄 Updated food: {item['name']} - {item['calories']} kcal")
        continue

    food = FoodMaster(
        id=uuid.uuid4(),
        name=item["name"],
        calories=item["calories"],
        unit=item["unit"],
        category=item["category"],
    )

    session.add(food)
    print(f"   ✅ Added food: {item['name']} - {item['calories']} kcal/{item['unit']}")

session.commit()

print(f"\n📊 Total food items in master database: {session.query(FoodMaster).count()}")

session.close()
print("\n🎉 Food master seeding completed!")
