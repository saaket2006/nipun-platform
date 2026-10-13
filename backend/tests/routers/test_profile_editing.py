from unittest.mock import patch
import pytest

from backend.models.models import User, CandidateProfile, RecruiterProfile
from backend.models.enums import UserRole, CompanyType
from backend.dependencies.auth_utils import get_password_hash
from backend.limiter import limiter


@pytest.fixture(autouse=True)
def disable_rate_limiting():
    """Temporarily disables SlowAPI rate limiting for unit tests."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture
def candidate_user(db_session):
    """Creates an active candidate with an existing CandidateProfile and null display_name."""
    user = User(
        firebase_uid="firebase_cand_123",
        email="candidate@example.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.CANDIDATE,
        profile_completed=True,
        display_name=None
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = CandidateProfile(
        user_id=user.id,
        current_status="Student",
        field_of_study="Computer Science",
        current_domain="Machine Learning"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return user


@pytest.fixture
def recruiter_user(db_session):
    """Creates an active recruiter with an existing RecruiterProfile and null display_name."""
    user = User(
        firebase_uid="firebase_rec_456",
        email="recruiter@example.com",
        hashed_password=get_password_hash("Password123!"),
        role=UserRole.RECRUITER,
        profile_completed=True,
        display_name=None
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    profile = RecruiterProfile(
        user_id=user.id,
        company_name="Acme Corp",
        company_type=CompanyType.STARTUP,
        hiring_domain="Software Engineering"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return user


# ==============================================================================
# CANDIDATE PROFILE TESTS
# ==============================================================================

def test_candidate_update_display_name(client, db_session, candidate_user):
    """Candidate can update display_name."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": "Jane Candidate"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Jane Candidate"
        assert data["email"] == "candidate@example.com"
        assert data["candidate_profile"]["current_status"] == "Student"

        # Verify DB
        db_user = db_session.query(User).filter(User.id == candidate_user.id).first()
        assert db_user.display_name == "Jane Candidate"


def test_candidate_update_profile_fields(client, db_session, candidate_user):
    """Candidate can update current_status, field_of_study, and current_domain."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "current_status": "Working Professional",
                "field_of_study": "Data Science",
                "current_domain": "Backend Systems"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["candidate_profile"]["current_status"] == "Working Professional"
        assert data["candidate_profile"]["field_of_study"] == "Data Science"
        assert data["candidate_profile"]["current_domain"] == "Backend Systems"

        # Verify DB
        prof = db_session.query(CandidateProfile).filter(CandidateProfile.user_id == candidate_user.id).first()
        assert prof.current_status == "Working Professional"
        assert prof.field_of_study == "Data Science"
        assert prof.current_domain == "Backend Systems"


def test_candidate_partial_update_preserves_omitted_fields(client, db_session, candidate_user):
    """Candidate partial update changes only provided field, preserving others."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"current_domain": "Cloud Architecture"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["candidate_profile"]["current_domain"] == "Cloud Architecture"
        assert data["candidate_profile"]["current_status"] == "Student"
        assert data["candidate_profile"]["field_of_study"] == "Computer Science"
        assert data["display_name"] is None


# ==============================================================================
# RECRUITER PROFILE TESTS
# ==============================================================================

def test_recruiter_update_display_name(client, db_session, recruiter_user):
    """Recruiter can update display_name."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_rec_456", "email": "recruiter@example.com"}
        response = client.patch(
            "/api/recruiter/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": "Bob Recruiter"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Bob Recruiter"
        assert data["recruiter_profile"]["company_name"] == "Acme Corp"

        # Verify DB
        db_user = db_session.query(User).filter(User.id == recruiter_user.id).first()
        assert db_user.display_name == "Bob Recruiter"


def test_recruiter_update_profile_fields(client, db_session, recruiter_user):
    """Recruiter can update company_name, company_type, and hiring_domain."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_rec_456", "email": "recruiter@example.com"}
        response = client.patch(
            "/api/recruiter/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={
                "company_name": "Global Tech Inc",
                "company_type": "Enterprise",
                "hiring_domain": "DevOps & Infrastructure"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["recruiter_profile"]["company_name"] == "Global Tech Inc"
        assert data["recruiter_profile"]["company_type"] == "Enterprise"
        assert data["recruiter_profile"]["hiring_domain"] == "DevOps & Infrastructure"

        # Verify DB
        prof = db_session.query(RecruiterProfile).filter(RecruiterProfile.user_id == recruiter_user.id).first()
        assert prof.company_name == "Global Tech Inc"
        assert prof.company_type == CompanyType.ENTERPRISE
        assert prof.hiring_domain == "DevOps & Infrastructure"


def test_recruiter_partial_update_preserves_omitted_fields(client, db_session, recruiter_user):
    """Recruiter partial update changes only provided field, preserving others."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_rec_456", "email": "recruiter@example.com"}
        response = client.patch(
            "/api/recruiter/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"company_name": "New Ventures Ltd"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["recruiter_profile"]["company_name"] == "New Ventures Ltd"
        assert data["recruiter_profile"]["company_type"] == "Startup"
        assert data["recruiter_profile"]["hiring_domain"] == "Software Engineering"
        assert data["display_name"] is None


# ==============================================================================
# SECURITY & RBAC TESTS
# ==============================================================================

def test_unauthenticated_patch_rejected(client):
    """Unauthenticated PATCH requests return 401."""
    resp1 = client.patch("/api/candidate/profile", json={"display_name": "Ghost"})
    assert resp1.status_code == 401

    resp2 = client.patch("/api/recruiter/profile", json={"display_name": "Ghost"})
    assert resp2.status_code == 401


def test_candidate_cannot_access_recruiter_patch(client, candidate_user):
    """A Candidate cannot update recruiter profile (403 Forbidden)."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/recruiter/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"company_name": "Hacked Corp"}
        )
        assert response.status_code == 403
        assert "Recruiter access required" in response.json()["detail"]


def test_recruiter_cannot_access_candidate_patch(client, recruiter_user):
    """A Recruiter cannot update candidate profile (403 Forbidden)."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_rec_456", "email": "recruiter@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"current_status": "Student"}
        )
        assert response.status_code == 403
        assert "Candidate access required" in response.json()["detail"]


@pytest.mark.parametrize("forbidden_field,value", [
    ("user_id", 999),
    ("id", 999),
    ("email", "malicious@attacker.com"),
    ("firebase_uid", "fake_firebase_uid"),
    ("role", "RECRUITER"),
    ("hashed_password", "fake_hash"),
    ("password", "newpassword123"),
    ("profile_completed", False),
    ("is_admin", True),
])
def test_candidate_patch_rejects_forbidden_fields(client, candidate_user, forbidden_field, value):
    """PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": "Valid Name", forbidden_field: value}
        )
        assert response.status_code == 422


@pytest.mark.parametrize("forbidden_field,value", [
    ("user_id", 999),
    ("id", 999),
    ("email", "malicious@attacker.com"),
    ("firebase_uid", "fake_firebase_uid"),
    ("role", "CANDIDATE"),
    ("hashed_password", "fake_hash"),
    ("password", "newpassword123"),
    ("profile_completed", False),
    ("is_admin", True),
])
def test_recruiter_patch_rejects_forbidden_fields(client, recruiter_user, forbidden_field, value):
    """PATCH endpoint rejects unknown/forbidden fields with 422 Unprocessable Entity."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_rec_456", "email": "recruiter@example.com"}
        response = client.patch(
            "/api/recruiter/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"company_name": "Valid Company", forbidden_field: value}
        )
        assert response.status_code == 422


# ==============================================================================
# VALIDATION TESTS
# ==============================================================================

def test_empty_display_name_rejected(client, candidate_user):
    """Empty display_name is rejected with 422."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": ""}
        )
        assert response.status_code == 422


def test_whitespace_only_display_name_rejected(client, candidate_user):
    """Whitespace-only display_name is rejected with 422."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": "     "}
        )
        assert response.status_code == 422


def test_null_display_name_in_patch_rejected(client, candidate_user):
    """Explicitly passing null display_name in PATCH is rejected to prevent erasing name."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": None}
        )
        assert response.status_code == 422


def test_display_name_whitespace_trimmed(client, db_session, candidate_user):
    """Leading and trailing whitespace is automatically stripped."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": "   Alice Wonderland   "}
        )
        assert response.status_code == 200
        assert response.json()["display_name"] == "Alice Wonderland"

        db_user = db_session.query(User).filter(User.id == candidate_user.id).first()
        assert db_user.display_name == "Alice Wonderland"


def test_excessively_long_display_name_rejected(client, candidate_user):
    """Display name exceeding 255 characters is rejected with 422."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.patch(
            "/api/candidate/profile",
            headers={"Authorization": "Bearer valid_token"},
            json={"display_name": "A" * 256}
        )
        assert response.status_code == 422


# ==============================================================================
# GET /api/profile REGRESSION & FALLBACK TESTS
# ==============================================================================

def test_get_profile_null_display_name_backward_compatibility(client, candidate_user):
    """Existing users with NULL display_name return display_name: null without error."""
    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_cand_123", "email": "candidate@example.com"}
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] is None
        assert data["email"] == "candidate@example.com"
        assert data["role"] == "CANDIDATE"
        assert data["candidate_profile"] is not None


def test_get_profile_with_display_name(client, db_session, recruiter_user):
    """User with populated display_name has display_name returned properly."""
    recruiter_user.display_name = "Chief Talent Officer"
    db_session.commit()

    with patch("backend.dependencies.auth_deps.verify_firebase_id_token") as mock_verify:
        mock_verify.return_value = {"uid": "firebase_rec_456", "email": "recruiter@example.com"}
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Chief Talent Officer"
        assert data["recruiter_profile"]["company_name"] == "Acme Corp"
