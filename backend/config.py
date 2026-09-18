import os
from typing import List, Set
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # API Settings
    API_TITLE: str = os.getenv("API_TITLE", "Nipun API")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    
    # CORS Settings
    _raw_origins: str = os.getenv("ALLOWED_ORIGINS", "")
    ALLOWED_ORIGINS: List[str] = (
        [origin.strip() for origin in _raw_origins.split(",") if origin.strip()]
        if _raw_origins.strip()
        else [
            "http://localhost:3000",
            "http://localhost:5000",
            "http://localhost:5500",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5000",
            "http://127.0.0.1:5500",
            "http://127.0.0.1:8000",
            "https://ai-resume-screener-69d23.web.app",
            "https://ai-resume-screener-69d23.firebaseapp.com",
            "https://nipun-platform.web.app",
            "https://nipun-platform.firebaseapp.com",
        ]
    )
    
    # Rate Limiting
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "5/minute")
    
    # File Upload Limits
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", str(5 * 1024 * 1024))) # Default 5MB
    
    ALLOWED_EXTENSIONS: Set[str] = {
        ext.strip().lower() for ext in os.getenv("ALLOWED_EXTENSIONS", ".pdf,.docx").split(",") if ext.strip()
    }
    
    # Log Level
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Database Settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # JWT Authentication Settings (Legacy fallback)
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRY_MINUTES: int = int(os.getenv("JWT_EXPIRY_MINUTES", "1440")) # Default 24 hours
    
    # Firebase Authentication & Admin Settings
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", os.getenv("VITE_FIREBASE_PROJECT_ID", "nipun-platform"))
    FIREBASE_CREDENTIALS_JSON: str = os.getenv("FIREBASE_CREDENTIALS_JSON", "")
    FIREBASE_SERVICE_ACCOUNT_KEY: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "")
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH", "")
    
    # Email & SMTP Settings
    EMAIL_USER: str = os.getenv("EMAIL_USER", "")
    EMAIL_PASS: str = os.getenv("EMAIL_PASS", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    
    # Frontend Base URL (for reset links)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://nipun-platform.web.app")
    
    # Password Reset Security Settings
    PASSWORD_RESET_EXPIRY_MINUTES: int = int(os.getenv("PASSWORD_RESET_EXPIRY_MINUTES", "30"))
    LOG_RESET_TOKENS: bool = os.getenv("LOG_RESET_TOKENS", "False").lower() in ("true", "1", "yes")


settings = Settings()

