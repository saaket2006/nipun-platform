import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from backend.database.database import get_db
from backend.models.models import User
from backend.models.enums import UserRole
from backend.core.firebase import verify_firebase_id_token

logger = logging.getLogger("resume_screener")

# Declare OAuth2 Bearer scheme (tokenUrl retained for OpenAPI docs compatibility)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Validates the incoming Firebase ID token using Firebase Admin SDK,
    extracts the server-verified Firebase UID, and resolves the corresponding PostgreSQL User.

    Security Boundaries:
    - Never accepts firebase_uid from client payloads or request parameters.
    - Resolves identity strictly via server-verified Firebase token claims.
    - Supports Just-In-Time (JIT) provisioning for newly authenticated Firebase users.
    - Handles concurrent insert race conditions gracefully with rollback recovery.
    """
    decoded_token = verify_firebase_id_token(token)

    uid = decoded_token.get("uid")
    if not uid:
        logger.warning("Token verification succeeded but missing 'uid' claim in token payload.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing trusted user identity claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_email: Optional[str] = decoded_token.get("email")
    email = raw_email.strip() if raw_email else None

    # 1. Primary Lookup: Resolve user exclusively by firebase_uid
    user = db.query(User).filter(User.firebase_uid == uid).first()

    # 2. Temporary Dev Transition Linking: Match existing dev accounts where firebase_uid IS NULL
    if not user and email:
        user = db.query(User).filter(
            func.lower(User.email) == email.lower(),
            User.firebase_uid.is_(None)
        ).first()

        if user:
            logger.info("Linking Firebase UID %s to pre-existing PostgreSQL user: %s", uid, user.email)
            user.firebase_uid = uid
            try:
                db.commit()
                db.refresh(user)
            except IntegrityError:
                db.rollback()
                user = db.query(User).filter(User.firebase_uid == uid).first()

    # 3. Just-In-Time (JIT) Provisioning: Create new application user if not found in PostgreSQL
    if not user:
        fallback_email = email or f"{uid}@firebase.user"
        logger.info("JIT provisioning new PostgreSQL user for Firebase UID %s (email: %s)", uid, fallback_email)
        user = User(
            firebase_uid=uid,
            email=fallback_email,
            role=UserRole.UNASSIGNED,
            profile_completed=False
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            # Handle race condition where a simultaneous concurrent request inserted the user
            db.rollback()
            user = db.query(User).filter(User.firebase_uid == uid).first()
            if not user:
                logger.error("Failed to recover user after concurrent provisioning collision for UID: %s", uid)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error resolving user account."
                )

    # 4. Synchronize email if user changed email in Firebase
    if email and user.email.strip().lower() != email.strip().lower():
        logger.info("Synchronizing updated email for user %s -> %s", user.email, email)
        user.email = email
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            logger.warning("Could not synchronize email %s for UID %s due to unique constraint collision.", email, uid)

    return user


def require_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """Restricts route access to users registered with the RECRUITER role in PostgreSQL."""
    if current_user.role != UserRole.RECRUITER:
        logger.warning(
            "Access denied: User %s does not have RECRUITER role (current role: %s)",
            current_user.email,
            current_user.role
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Recruiter access required"
        )
    return current_user


def require_candidate(current_user: User = Depends(get_current_user)) -> User:
    """Restricts route access to users registered with the CANDIDATE role in PostgreSQL."""
    if current_user.role != UserRole.CANDIDATE:
        logger.warning(
            "Access denied: User %s does not have CANDIDATE role (current role: %s)",
            current_user.email,
            current_user.role
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Candidate access required"
        )
    return current_user
