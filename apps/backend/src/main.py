"""Điểm vào ứng dụng FastAPI chính."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

from .auth.router import router as auth_router

from .config import settings

# Import models để đảm bảo chúng được tạo trong database
from .models import User, AuthAuditLog, FailedLoginAttempt, UserProfile


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API cho hệ thống cơ sở Crypto",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware
cors_origins = ["*"] if settings.DEBUG else settings.ALLOWED_ORIGINS
print(f"CORS Origins: {cors_origins}")
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Debug: {settings.DEBUG}")

# Production CORS configuration
if settings.ENVIRONMENT == "production":
    # Use configured allowed origins for production
    cors_origins = settings.ALLOWED_ORIGINS
    print(f"Production CORS Origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/cors-test")
async def cors_test():
    return {
        "message": "CORS test successful",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "cors_origins_config": settings.CORS_ORIGINS
    }

@app.get("/debug")
async def debug_info():
    import os
    return {
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "database_url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else None,
        "redis_url": settings.REDIS_URL,
        "allowed_origins": settings.ALLOWED_ORIGINS,
        "env_vars": {
            "DATABASE_URL": os.getenv("DATABASE_URL", "NOT_SET")[:20] + "..." if os.getenv("DATABASE_URL") else "NOT_SET",
            "REDIS_URL": os.getenv("REDIS_URL", "NOT_SET"),
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "NOT_SET"),
            "DEBUG": os.getenv("DEBUG", "NOT_SET")
        }
    }

@app.get("/debug/db")
async def debug_database():
    """Debug database connection and tables"""
    try:
        from sqlalchemy import text
        from .database import get_db
        
        db = next(get_db())
        
        # Check if tables exist
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables_result = db.execute(tables_query)
        tables = [row[0] for row in tables_result]
        
        # Check alembic version
        try:
            version_query = text("SELECT version_num FROM alembic_version")
            version_result = db.execute(version_query)
            current_version = version_result.scalar()
        except Exception as e:
            current_version = f"Error: {str(e)}"
        
        return {
            "status": "connected",
            "tables": tables,
            "alembic_version": current_version,
            "failed_login_table_exists": "failedloginattempts" in tables
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@app.options("/cors-test")
async def cors_test():
    """Test CORS preflight request"""
    return {"message": "CORS preflight successful"}

@app.get("/cors-test")
async def cors_test_get():
    """Test CORS GET request"""
    return {"message": "CORS GET successful"}

@app.get("/")
async def root():
    return {
        "message": "Crypto Base API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    } 