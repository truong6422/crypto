"""Authentication router."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, UserProfile
from . import schemas
from .service import AuthService
from .dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    login_data: schemas.LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user."""
    auth_service = AuthService(db)
    return auth_service.login(login_data, request)


@router.post("/logout")
def logout(
    logout_data: schemas.LogoutRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Logout user."""
    auth_service = AuthService(db)
    return auth_service.logout(logout_data.refresh_token, request)


@router.post("/refresh", response_model=schemas.RefreshResponse)
def refresh_token(
    refresh_data: schemas.RefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_data.refresh_token)


@router.post("/register", response_model=schemas.RegisterResponse)
def register(
    register_data: schemas.RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register new user with basic information."""
    auth_service = AuthService(db)
    return auth_service.register(register_data, request)


@router.get("/me")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


@router.get("/check-users")
def check_users(db: Session = Depends(get_db)):
    """Check if there are any users in the database."""
    users = db.query(User).all()
    return {
        "total_users": len(users),
        "users": [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active
            }
            for user in users
        ]
    }


@router.post("/seed-demo-users")
def seed_demo_users(db: Session = Depends(get_db)):
    """Seed demo users for testing."""
    try:
        from ..auth.service import AuthService
        from ..auth.schemas import UserCreate
        
        auth_service = AuthService(db)
        
        # Demo users data
        demo_users = [
            {
                "username": "admin",
                "email": "admin@cryptobase.com",
                "full_name": "Administrator",
                "password": "admin123"
            },


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
        
        return {
            "message": "Demo users seeded successfully",
            "created_count": len(created_users),
            "demo_credentials": {
                "admin": "admin123",

            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding demo users: {str(e)}")


@router.get("/profile", response_model=schemas.UserProfileResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # Create empty profile if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


@router.put("/profile", response_model=schemas.UserProfileResponse)
def update_user_profile(
    profile_data: schemas.UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    
    if not profile:
        # Create new profile if doesn't exist
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Update fields
    if profile_data.phone is not None:
        profile.phone = profile_data.phone
    if profile_data.address is not None:
        profile.address = profile_data.address
    if profile_data.bio is not None:
        profile.bio = profile_data.bio
    if profile_data.date_of_birth is not None:
        profile.date_of_birth = profile_data.date_of_birth
    if profile_data.gender is not None:
        profile.gender = profile_data.gender
    if profile_data.preferences is not None:
        profile.preferences = profile_data.preferences
    
    db.commit()
    db.refresh(profile)
    
    return profile


@router.put("/me", response_model=dict)
def update_current_user_info(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information (email, full_name, avatar_url)."""
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id,
            User.is_deleted == False
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email đã được sử dụng bởi người dùng khác"
            )
        current_user.email = user_update.email
    
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    if user_update.avatar_url is not None:
        current_user.avatar_url = user_update.avatar_url
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
        "avatar_url": current_user.avatar_url,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    } 