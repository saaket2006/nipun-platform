import os
import pytest
from unittest.mock import patch

def test_cors_origins_prod(monkeypatch):
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("ALLOWED_ORIGINS", "")

    # Reload settings module to re-evaluate module level variables
    import importlib
    import backend.config
    importlib.reload(backend.config)

    settings = backend.config.Settings()

    assert "http://localhost:3000" not in settings.ALLOWED_ORIGINS
    assert "https://nipun-platform.web.app" in settings.ALLOWED_ORIGINS

def test_cors_origins_dev(monkeypatch):
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("ALLOWED_ORIGINS", "")

    # Reload settings module
    import importlib
    import backend.config
    importlib.reload(backend.config)

    settings = backend.config.Settings()

    assert "http://localhost:3000" in settings.ALLOWED_ORIGINS
    assert "https://nipun-platform.web.app" in settings.ALLOWED_ORIGINS

def test_cors_origins_custom(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "http://test.com, http://example.com")

    # Reload settings module
    import importlib
    import backend.config
    importlib.reload(backend.config)

    settings = backend.config.Settings()

    assert settings.ALLOWED_ORIGINS == ["http://test.com", "http://example.com"]
