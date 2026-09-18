import logging
from fastapi import FastAPI, UploadFile, File, Form, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware

# Initialize central config and logging
from backend.config import settings
from backend.logging_config import setup_logging

setup_logging(settings.LOG_LEVEL)

logger = logging.getLogger("resume_screener")

# Startup configuration validation
if not settings.FIREBASE_PROJECT_ID:
    logger.warning("Startup Configuration Warning: FIREBASE_PROJECT_ID is not configured.")

# Initialize Firebase Admin SDK (lazy singleton)
try:
    from backend.core.firebase import get_firebase_admin_app
    get_firebase_admin_app()
except Exception as fb_err:
    logger.critical("Firebase Admin initialization encountered an error at startup: %s", fb_err)


# Initialize Rate Limiter
from backend.limiter import limiter

# Import Routers
from backend.routers import auth, candidate, recruiter, onboarding
from backend.dependencies.auth_deps import require_recruiter
from backend.models.models import User
from backend.schemas.schemas import UserProfileResponse
from backend.dependencies.auth_deps import get_current_user

app = FastAPI(title=settings.API_TITLE)

@app.on_event("startup")
def startup_event():
    """Startup event handler: verify database connectivity and seed default profiles."""
    try:
        from backend.database.database import check_db_connection, SessionLocal
        from backend.services.policy.default_profiles import seed_default_profiles

        if check_db_connection():
            db = SessionLocal()
            try:
                seed_default_profiles(db)
                logger.info("Startup Validation: Database seeded with default profiles successfully.")
            except Exception as e:
                logger.error("Could not seed default profiles: %s", e)
            finally:
                db.close()
        else:
            logger.warning("Database connection unavailable at startup. Application will start in degraded mode.")
    except Exception as e:
        logger.error("Startup Validation Error during database initialization: %s", e)

# Set up Rate Limiting Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Set up CORS Middleware using centralized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)


# Root and Health check endpoints
@app.get("/")
def read_root():
    return {"message": "Nipun API running."}


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}


# Register Modular Routers
app.include_router(auth.router, prefix="/api")
app.include_router(candidate.router, prefix="/api")
app.include_router(recruiter.router, prefix="/api")
app.include_router(onboarding.router, prefix="/api")


# Profile Endpoint (retrieves full nested profile details for dashboards)
@app.get("/api/profile", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Retrieves the full profile details of the authenticated user."""
    logger.info("Profile retrieval requested for user: %s", current_user.email)
    return current_user


from sqlalchemy.orm import Session
from backend.database.database import get_db


# Legacy Route for 100% backward compatibility
# Delegate directly to the process_resumes function from recruiter router
@app.post("/api/process")
@limiter.limit(settings.RATE_LIMIT)
async def legacy_process_resumes(
    request: Request,
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...),
    current_user: User = Depends(require_recruiter),
    db: Session = Depends(get_db),
):
    """Legacy endpoint delegating to recruiter process_resumes. Requires Recruiter authentication."""
    logger.info(
        "Legacy endpoint /api/process called by recruiter: %s. Routing to recruiter service...",
        current_user.email,
    )
    return await recruiter.process_resumes(
        request=request,
        job_description=job_description,
        resumes=resumes,
        current_user=current_user,
        db=db,
    )
