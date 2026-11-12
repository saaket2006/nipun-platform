import pytest
from unittest.mock import MagicMock
from starlette.testclient import TestClient
from backend.main import app
from backend.config import Settings
from backend.dependencies.auth_deps import get_current_user
from backend.models.models import User, UserRole

client = TestClient(app)

DEV_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8085",
    "http://127.0.0.1:8085",
]

PROD_ORIGINS = [
    "https://ai-resume-screener-69d23.web.app",
    "https://ai-resume-screener-69d23.firebaseapp.com",
    "https://nipun-platform.web.app",
    "https://nipun-platform.firebaseapp.com",
]

def test_settings_allowed_origins_dev_mode(monkeypatch):
    """Verify that in development mode (DEBUG=True), allowed origins include both dev and prod origins."""
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    
    settings = Settings()
    for origin in DEV_ORIGINS:
        assert origin in settings.ALLOWED_ORIGINS, f"Missing dev origin in dev mode: {origin}"
    for origin in PROD_ORIGINS:
        assert origin in settings.ALLOWED_ORIGINS, f"Missing prod origin in dev mode: {origin}"

def test_settings_allowed_origins_prod_mode(monkeypatch):
    """Verify that in production mode (DEBUG=False), dev origins are excluded and prod origins are included."""
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    
    settings = Settings()
    for origin in DEV_ORIGINS:
        assert origin not in settings.ALLOWED_ORIGINS, f"Dev origin should not be in prod mode: {origin}"
    for origin in PROD_ORIGINS:
        assert origin in settings.ALLOWED_ORIGINS, f"Missing prod origin in prod mode: {origin}"

def test_explicit_env_override_allowed_origins(monkeypatch):
    """Verify that when ALLOWED_ORIGINS env var is provided, it is parsed and honored regardless of DEBUG mode."""
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://custom.domain.com, http://localhost:3000")
    settings = Settings()
    assert settings.ALLOWED_ORIGINS == ["https://custom.domain.com", "http://localhost:3000"]

@pytest.mark.parametrize("origin", [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8085",
    "http://127.0.0.1:8085",
    "https://nipun-platform.web.app",
    "https://nipun-platform.firebaseapp.com",
    "https://ai-resume-screener-69d23.web.app",
    "https://ai-resume-screener-69d23.firebaseapp.com",
])
def test_preflight_options_allowed_origins(origin):
    """Verify that OPTIONS preflight requests from all supported local dev and prod origins succeed with 200."""
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization, content-type, x-requested-with",
        },
    )
    assert response.status_code == 200, f"Preflight failed for {origin}: status {response.status_code}, text: {response.text}"
    assert response.headers.get("access-control-allow-origin") == origin
    assert response.headers.get("access-control-allow-credentials") == "true"
    
    allow_methods = response.headers.get("access-control-allow-methods", "")
    assert "GET" in allow_methods
    assert "OPTIONS" in allow_methods
    assert "HEAD" in allow_methods
    
    allow_headers = response.headers.get("access-control-allow-headers", "").lower()
    assert "authorization" in allow_headers
    assert "content-type" in allow_headers

def test_preflight_options_disallowed_origin():
    """Verify that untrusted origins do not receive CORS permission."""
    disallowed_origin = "http://malicious-site.example.com"
    response = client.options(
        "/api/auth/me",
        headers={
            "Origin": disallowed_origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization, content-type",
        },
    )
    # Starlette CORSMiddleware returns 400 for disallowed origin in preflight
    assert response.status_code == 400 or "access-control-allow-origin" not in response.headers
    assert response.headers.get("access-control-allow-origin") != disallowed_origin

def test_actual_unauthenticated_request_cors_headers_on_localhost_3000():
    """Verify that an unauthenticated GET request from http://localhost:3000 includes CORS headers on 401 response."""
    response = client.get(
        "/api/auth/me",
        headers={
            "Origin": "http://localhost:3000",
        },
    )
    assert response.status_code == 401
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_actual_authenticated_request_cors_headers_on_localhost_3000():
    """Verify that an authenticated GET request from http://localhost:3000 succeeds with 200 and includes CORS headers."""
    from datetime import datetime, timezone

    mock_user = MagicMock(spec=User)
    mock_user.id = 42
    mock_user.email = "test.candidate@example.com"
    mock_user.display_name = "Test Candidate"
    mock_user.role = UserRole.CANDIDATE
    mock_user.firebase_uid = "mock-firebase-uid-123"
    mock_user.profile_completed = True
    mock_user.created_at = datetime.now(timezone.utc)
    mock_user.updated_at = datetime.now(timezone.utc)

    app.dependency_overrides[get_current_user] = lambda: mock_user
    try:
        response = client.get(
            "/api/auth/me",
            headers={
                "Origin": "http://localhost:3000",
                "Authorization": "Bearer mock-valid-token",
            },
        )
        assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert response.headers.get("access-control-allow-credentials") == "true"
        
        data = response.json()
        assert data["email"] == "test.candidate@example.com"
        assert data["role"].lower() == "candidate"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
