import os
import json
import base64
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

import firebase_admin
from firebase_admin import credentials, auth

from backend.config import settings

logger = logging.getLogger("resume_screener")

_firebase_app: Optional[firebase_admin.App] = None
_init_error: Optional[str] = None


def get_firebase_admin_app() -> Optional[firebase_admin.App]:
    """
    Lazily initializes and returns the singleton Firebase Admin App.
    Supports:
    1. FIREBASE_CREDENTIALS_JSON or FIREBASE_SERVICE_ACCOUNT_KEY as a JSON string (Render / cloud deployment)
    2. FIREBASE_CREDENTIALS_JSON or FIREBASE_SERVICE_ACCOUNT_KEY as a base64 encoded JSON string
    3. FIREBASE_SERVICE_ACCOUNT_KEY_PATH or FIREBASE_SERVICE_ACCOUNT_KEY as a local file path
    4. Application Default Credentials with FIREBASE_PROJECT_ID
    """
    global _firebase_app, _init_error

    if _firebase_app is not None:
        return _firebase_app

    # Check if already initialized by default
    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app

    raw_key = (
        settings.FIREBASE_CREDENTIALS_JSON.strip()
        or settings.FIREBASE_SERVICE_ACCOUNT_KEY.strip()
        or settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH.strip()
    )
    project_id = settings.FIREBASE_PROJECT_ID.strip()

    try:
        cred = None
        if raw_key:
            # 1. Check if the string is base64-encoded JSON
            if not raw_key.startswith("{") and not os.path.exists(raw_key):
                try:
                    decoded_bytes = base64.b64decode(raw_key)
                    decoded_str = decoded_bytes.decode("utf-8").strip()
                    if decoded_str.startswith("{") and decoded_str.endswith("}"):
                        raw_key = decoded_str
                        logger.info("Decoded base64-encoded Firebase service account credential.")
                except Exception:
                    pass

            # 2. Try parsing raw JSON credential string
            if raw_key.startswith("{") and raw_key.endswith("}"):
                try:
                    key_dict = json.loads(raw_key)
                    cred = credentials.Certificate(key_dict)
                    logger.info("Initializing Firebase Admin SDK using JSON service account credential string.")
                except Exception as json_err:
                    logger.error("Failed to parse Firebase service account credentials as JSON: %s", json_err)
                    raise json_err
            # 3. Try loading from file path
            elif os.path.exists(raw_key):
                cred = credentials.Certificate(raw_key)
                logger.info("Initializing Firebase Admin SDK using service account file at: %s", raw_key)
            else:
                logger.warning(
                    "Firebase service account credential was provided but is neither valid JSON nor an existing file path."
                )

        if cred is not None:
            _firebase_app = firebase_admin.initialize_app(cred, options={"projectId": project_id} if project_id else None)
        else:
            # 3. Fallback to default credentials or project options
            logger.info("Initializing Firebase Admin SDK using project credentials for project: %s", project_id)
            if project_id:
                _firebase_app = firebase_admin.initialize_app(options={"projectId": project_id})
            else:
                _firebase_app = firebase_admin.initialize_app()

        _init_error = None
        logger.info("Firebase Admin SDK initialized successfully.")
        return _firebase_app

    except Exception as e:
        _init_error = str(e)
        logger.critical("Firebase Admin SDK initialization failed: %s", e)
        return None


DEFAULT_CLOCK_SKEW_SECONDS: int = 5


def verify_firebase_id_token(
    id_token: str,
    check_revoked: bool = False,
    clock_skew_seconds: int = DEFAULT_CLOCK_SKEW_SECONDS,
) -> Dict[str, Any]:
    """
    Verifies a Firebase ID token using the Firebase Admin SDK.
    Extracts trusted server-side claims including 'uid' and 'email'.
    Raises clean HTTP 401 for token issues and HTTP 503 for configuration errors without leaking secrets.
    Accepts clock_skew_seconds (default 5) to tolerate minor timestamp drift / network latency boundary gaps.
    """
    app = get_firebase_admin_app()
    if app is None:
        logger.error("Authentication failure: Firebase Admin is not initialized. Error: %s", _init_error)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is currently unavailable. Please contact system administrator."
        )

    if not id_token or not isinstance(id_token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        decoded_token = auth.verify_id_token(
            id_token,
            check_revoked=check_revoked,
            clock_skew_seconds=clock_skew_seconds,
        )
        return decoded_token

    except auth.RevokedIdTokenError as e:
        logger.warning("Firebase token verification failed (revoked): %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has been revoked. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.ExpiredIdTokenError as e:
        logger.info("Firebase token verification failed (expired): %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError as e:
        logger.warning("Firebase token verification failed (invalid): %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("Unexpected error during Firebase token verification: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
