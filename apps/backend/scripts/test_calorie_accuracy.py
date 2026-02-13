import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.meal_planning.models import FoodMaster

db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/meal")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()


def calculate_calories(calories_per_100g, amount):
    return (calories_per_100g / 100) * amount


def run_test_iteration(iteration):
    print(f"\n--- Iteration {iteration + 1} ---")

    test_cases = [
        {"name": "Gạo nếp cái", "amount": 200, "expected": 688.0},
        {"name": "Thịt bò loại 1", "amount": 250, "expected": 295.0},
        {"name": "Trứng gà", "amount": 150, "expected": 249.0},
        {"name": "Súp lơ xanh", "amount": 300, "expected": 78.0},
        {"name": "Dưa hấu", "amount": 500, "expected": 80.0},
    ]

    success_count = 0
    for case in test_cases:
        food = session.query(FoodMaster).filter(FoodMaster.name == case["name"]).first()
        if not food:
            print(f"   ❌ Food not found: {case['name']}")
            continue

        actual = calculate_calories(food.calories, case["amount"])
        if actual == case["expected"]:
            print(
                f"   ✅ {case['name']} ({case['amount']}g): Expected {case['expected']}, Got {actual}"
            )
            success_count += 1
        else:
            print(
                f"   ❌ {case['name']} ({case['amount']}g): Expected {case['expected']}, Got {actual}"
            )

    return success_count == len(test_cases)


print("🧪 Starting calorie calculation accuracy tests (10 iterations)...")

all_passed = True
for i in range(10):
    if not run_test_iteration(i):
        all_passed = False

if all_passed:
    print(
        "\n🌟 ALL TESTS PASSED! Calorie calculation is accurate across 10 iterations."
    )
else:
    print("\n⚠️ SOME TESTS FAILED. Please check the logs.")

session.close()
