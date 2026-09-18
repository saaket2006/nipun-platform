import pytest
from unittest.mock import patch
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from backend.models.models import User
from backend.models.enums import UserRole
from backend.dependencies.auth_deps import get_current_user, require_recruiter, require_candidate
from backend.core.firebase import verify_firebase_id_token


def test_get_current_user_existing_firebase_uid(db_session):
    """Verifies that a user with an existing firebase_uid is resolved directly."""
    existing_user = User(
        firebase_uid="firebase_uid_123",
        email="existing@example.com",
        role=UserRole.CANDIDATE,
        profile_completed=True
    )
    db_session.add(existing_user)
    db_session.commit()

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "firebase_uid_123",
            "email": "existing@example.com"
        }
        resolved_user = get_current_user(token="valid_token", db=db_session)
        assert resolved_user.id == existing_user.id
        assert resolved_user.firebase_uid == "firebase_uid_123"
        assert resolved_user.role == UserRole.CANDIDATE


def test_get_current_user_dev_transition_linking(db_session):
    """Verifies that an existing dev user matching email is linked to the Firebase UID."""
    legacy_user = User(
        firebase_uid=None,
        email="legacy@example.com",
        role=UserRole.RECRUITER,
        profile_completed=True
    )
    db_session.add(legacy_user)
    db_session.commit()

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "firebase_uid_legacy_456",
            "email": "LEGACY@EXAMPLE.COM"  # Case-insensitive check
        }
        resolved_user = get_current_user(token="valid_token", db=db_session)
        assert resolved_user.id == legacy_user.id
        assert resolved_user.firebase_uid == "firebase_uid_legacy_456"
        assert resolved_user.email == "legacy@example.com"


def test_get_current_user_no_email_claim_does_not_link(db_session):
    """Verifies that if the token lacks an email claim, it does not link to existing rows by email."""
    legacy_user = User(
        firebase_uid=None,
        email="unclaimed@example.com",
        role=UserRole.RECRUITER,
        profile_completed=True
    )
    db_session.add(legacy_user)
    db_session.commit()

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "firebase_uid_no_email_789"
            # No email claim
        }
        resolved_user = get_current_user(token="valid_token", db=db_session)
        # Should JIT-provision a new user rather than stealing legacy_user
        assert resolved_user.id != legacy_user.id
        assert resolved_user.firebase_uid == "firebase_uid_no_email_789"
        assert resolved_user.role == UserRole.UNASSIGNED


def test_get_current_user_jit_provisioning(db_session):
    """Verifies that a new Firebase user is automatically JIT-provisioned in PostgreSQL."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "brand_new_uid_999",
            "email": "newuser@example.com"
        }
        resolved_user = get_current_user(token="valid_token", db=db_session)
        assert resolved_user.id is not None
        assert resolved_user.firebase_uid == "brand_new_uid_999"
        assert resolved_user.email == "newuser@example.com"
        assert resolved_user.role == UserRole.UNASSIGNED
        assert resolved_user.profile_completed is False


def test_get_current_user_missing_uid_claim(db_session):
    """Verifies that a token without a uid claim is rejected with HTTP 401."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"email": "nouid@example.com"}
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token="token_without_uid", db=db_session)
        assert exc_info.value.status_code == 401


def test_require_recruiter_guard():
    """Verifies that require_recruiter accepts recruiters and rejects non-recruiters with 403."""
    recruiter = User(id=1, email="rec@example.com", role=UserRole.RECRUITER)
    candidate = User(id=2, email="cand@example.com", role=UserRole.CANDIDATE)
    unassigned = User(id=3, email="unassigned@example.com", role=UserRole.UNASSIGNED)

    assert require_recruiter(current_user=recruiter) == recruiter

    with pytest.raises(HTTPException) as exc_info1:
        require_recruiter(current_user=candidate)
    assert exc_info1.value.status_code == 403

    with pytest.raises(HTTPException) as exc_info2:
        require_recruiter(current_user=unassigned)
    assert exc_info2.value.status_code == 403


def test_require_candidate_guard():
    """Verifies that require_candidate accepts candidates and rejects non-candidates with 403."""
    recruiter = User(id=1, email="rec@example.com", role=UserRole.RECRUITER)
    candidate = User(id=2, email="cand@example.com", role=UserRole.CANDIDATE)

    assert require_candidate(current_user=candidate) == candidate

    with pytest.raises(HTTPException) as exc_info:
        require_candidate(current_user=recruiter)
    assert exc_info.value.status_code == 403


def test_api_me_endpoint(client, db_session):
    """Verifies GET /api/auth/me returns PostgreSQL user info when authenticated via Firebase ID token."""
    user = User(
        firebase_uid="uid_for_me_test",
        email="me_user@example.com",
        role=UserRole.RECRUITER,
        profile_completed=True
    )
    db_session.add(user)
    db_session.commit()

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {
            "uid": "uid_for_me_test",
            "email": "me_user@example.com"
        }
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer fake_token"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me_user@example.com"
        assert data["role"] == "RECRUITER"
        assert data["profile_completed"] is True
        assert "firebase_uid" not in data  # Ensure internal UID is not leaked


def test_verify_firebase_id_token_empty():
    """Verifies that an empty or non-string token raises HTTP 401."""
    with patch("backend.core.firebase.get_firebase_admin_app") as mock_get_app:
        mock_get_app.return_value = object()
        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_id_token("")
        assert exc_info.value.status_code == 401


def test_verify_firebase_id_token_uninitialized_service():
    """Verifies that if Firebase Admin fails to initialize, verify_id_token raises HTTP 503."""
    with patch("backend.core.firebase.get_firebase_admin_app", return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_id_token("some_token")
        assert exc_info.value.status_code == 503


def test_get_firebase_admin_app_base64_decoding():
    """Verifies that base64-encoded credentials JSON is successfully decoded."""
    import base64
    import json
    import backend.core.firebase as fb_module

    # Reset module singleton
    old_app = fb_module._firebase_app
    fb_module._firebase_app = None

    test_cred = {"type": "service_account", "project_id": "test-b64-project"}
    raw_json = json.dumps(test_cred)
    b64_str = base64.b64encode(raw_json.encode("utf-8")).decode("utf-8")

    try:
        with patch("backend.core.firebase.settings") as mock_settings, \
             patch("backend.core.firebase.credentials.Certificate") as mock_cert, \
             patch("backend.core.firebase.firebase_admin.initialize_app") as mock_init, \
             patch("backend.core.firebase.firebase_admin._apps", {}):

            mock_settings.FIREBASE_CREDENTIALS_JSON = b64_str
            mock_settings.FIREBASE_SERVICE_ACCOUNT_KEY = ""
            mock_settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH = ""
            mock_settings.FIREBASE_PROJECT_ID = "test-b64-project"

            app = fb_module.get_firebase_admin_app()
            mock_cert.assert_called_once_with(test_cred)
            mock_init.assert_called_once()
    finally:
        fb_module._firebase_app = old_app


# ==============================================================================
# CLOCK SKEW & TOKEN VERIFICATION REGRESSION TESTS
# ==============================================================================

def test_verify_firebase_id_token_passes_clock_skew():
    """Verifies that verify_firebase_id_token forwards clock_skew_seconds=5 to auth.verify_id_token."""
    with patch("backend.core.firebase.get_firebase_admin_app", return_value=object()), \
         patch("backend.core.firebase.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "user_skew_test", "email": "skew@example.com"}

        result = verify_firebase_id_token("mock_token_123")
        assert result["uid"] == "user_skew_test"
        mock_verify.assert_called_once_with("mock_token_123", check_revoked=False, clock_skew_seconds=5)


def test_verify_firebase_id_token_custom_clock_skew():
    """Verifies that verify_firebase_id_token allows custom clock_skew_seconds override."""
    with patch("backend.core.firebase.get_firebase_admin_app", return_value=object()), \
         patch("backend.core.firebase.auth.verify_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "user_skew_test", "email": "skew@example.com"}

        result = verify_firebase_id_token("mock_token_custom", check_revoked=True, clock_skew_seconds=10)
        assert result["uid"] == "user_skew_test"
        mock_verify.assert_called_once_with("mock_token_custom", check_revoked=True, clock_skew_seconds=10)


def test_verify_firebase_id_token_token_used_too_early_error():
    """Verifies that auth.InvalidIdTokenError for future timestamp outside tolerance raises HTTP 401."""
    from firebase_admin import auth as fb_auth

    with patch("backend.core.firebase.get_firebase_admin_app", return_value=object()), \
         patch("backend.core.firebase.auth.verify_id_token", side_effect=fb_auth.InvalidIdTokenError("Token used too early, 100 < 200.")):
        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_id_token("future_token")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication credentials."


def test_verify_firebase_id_token_expired_error():
    """Verifies that auth.ExpiredIdTokenError raises HTTP 401."""
    from firebase_admin import auth as fb_auth

    with patch("backend.core.firebase.get_firebase_admin_app", return_value=object()), \
         patch("backend.core.firebase.auth.verify_id_token", side_effect=fb_auth.ExpiredIdTokenError("Token expired", None)):
        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_id_token("expired_token")
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()


def test_verify_firebase_id_token_revoked_error():
    """Verifies that auth.RevokedIdTokenError raises HTTP 401."""
    from firebase_admin import auth as fb_auth

    with patch("backend.core.firebase.get_firebase_admin_app", return_value=object()), \
         patch("backend.core.firebase.auth.verify_id_token", side_effect=fb_auth.RevokedIdTokenError("Token revoked")):
        with pytest.raises(HTTPException) as exc_info:
            verify_firebase_id_token("revoked_token", check_revoked=True)
        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail.lower()


def test_google_auth_jwt_clock_skew_tolerance():
    """Directly verifies Google Auth JWT validation with clock_skew_in_seconds=5."""
    import time
    from google.auth import jwt as google_jwt
    from google.auth import exceptions as google_exceptions

    current_time = int(time.time())

    # 1. Token issued 2 seconds in the future (within 5-second clock skew tolerance)
    payload_within_skew = {
        "iat": current_time + 2,
        "exp": current_time + 3600,
    }
    # Must not raise an exception
    google_jwt._verify_iat_and_exp(payload_within_skew, clock_skew_in_seconds=5)

    # 2. Token issued 10 seconds in the future (outside 5-second tolerance)
    payload_outside_skew = {
        "iat": current_time + 10,
        "exp": current_time + 3600,
    }
    with pytest.raises(google_exceptions.InvalidValue, match="Token used too early"):
        google_jwt._verify_iat_and_exp(payload_outside_skew, clock_skew_in_seconds=5)

    # 3. Token expired 10 seconds ago (outside 5-second tolerance)
    payload_expired = {
        "iat": current_time - 3600,
        "exp": current_time - 10,
    }
    with pytest.raises(google_exceptions.InvalidValue, match="Token expired"):
        google_jwt._verify_iat_and_exp(payload_expired, clock_skew_in_seconds=5)

