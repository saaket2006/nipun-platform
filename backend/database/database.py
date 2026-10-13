import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings

logger = logging.getLogger("resume_screener")

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    logger.critical("Startup Configuration Failed: DATABASE_URL is not set.")
    # We won't raise RuntimeError here to allow the app to boot (e.g. for health checks)
    DATABASE_URL = "sqlite:///./fallback.db" # Fallback so SQLAlchemy doesn't crash on create_engine
else:
    # Normalize legacy postgres:// scheme to postgresql:// for SQLAlchemy compatibility
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    if not (
        DATABASE_URL.startswith("postgresql://")
        or DATABASE_URL.startswith("postgresql+")
    ):
        logger.critical("Startup Configuration Failed: ONLY PostgreSQL (Supabase) is supported. Received: %s", DATABASE_URL)

def create_db_engine(url: str):
    return create_engine(url, pool_pre_ping=True)

engine = create_db_engine(DATABASE_URL)

def check_db_connection() -> bool:
    """Tests connection to the configured database on demand (e.g. startup or health check)."""
    try:
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            pass
        logger.info("Database connection established successfully.")
        return True
    except Exception as e:
        logger.error("Database connection check failed: %s", e)
        return False

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI Dependency to yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
