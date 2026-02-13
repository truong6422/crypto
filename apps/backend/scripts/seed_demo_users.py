#!/usr/bin/env python3
"""Script để tạo demo users cho US-001."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_db, create_tables
from src.auth.service import AuthService
from src.auth.schemas import UserCreate


def create_demo_users():
    """Create demo users for testing."""
    print("Creating demo users...")
    
    # Create tables if they don't exist
    create_tables()
    
    # Get database session
    db = next(get_db())
    auth_service = AuthService(db)
    
    # Demo users data
    demo_users = [
        {
            "username": "admin",
            "email": "admin@dailymeals.com",
            "full_name": "Administrator",
            "password": "admin123"
        },
        {
            "username": "chef",
            "email": "chef@dailymeals.com", 
            "full_name": "Head Chef",
            "password": "chef123"
        },
        {
            "username": "nutritionist",
            "email": "nutritionist@dailymeals.com",
            "full_name": "Nutrition Expert",
            "password": "nutri123"
        }
    ]
    
    created_users = []
    
    for user_data in demo_users:
        try:
            # Check if user already exists
            existing_user = auth_service.get_user_by_username(user_data["username"])
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                continue
            
            # Create user
            user_create = UserCreate(**user_data)
            user = auth_service.create_user(user_create)
            created_users.append(user)
            print(f"Created user: {user.username} ({user.full_name})")
            
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {e}")
    
    print(f"\nDemo users created: {len(created_users)}")
    print("\nDemo credentials:")
    print("admin / admin123")
    print("chef / chef123") 
    print("nutritionist / nutri123")


if __name__ == "__main__":
    create_demo_users()
