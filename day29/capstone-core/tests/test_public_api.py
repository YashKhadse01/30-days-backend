"""Tests for public API security and documentation."""

import hashlib
from types import SimpleNamespace

from fastapi.testclient import TestClient

from capstone_core.api import public_api
from capstone_core.main import app

client = TestClient(app)

TEST_KEY = "test-api-key-123"


def configure_key(monkeypatch, value: str | None) -> None:
    monkeypatch.setattr(
        public_api,
        "get_settings",
        lambda: SimpleNamespace(api_key_sha256=value),
    )


def test_valid_api_key(monkeypatch) -> None:
    configure_key(
        monkeypatch,
        hashlib.sha256(TEST_KEY.encode()).hexdigest(),
    )

    from unittest.mock import AsyncMock

    from capstone_core.api import public_api

    original_get_settings = public_api.get_settings

    def settings_with_redis():
        settings = original_get_settings()
        settings.redis_url = "redis://localhost:6379/0"
        return settings

    monkeypatch.setattr(
        public_api,
        "get_settings",
        settings_with_redis,
    )

    redis = AsyncMock()
    monkeypatch.setattr(
        public_api.Redis,
        "from_url",
        lambda url: redis,
    )

    limiter = AsyncMock()
    limiter.allow.return_value = True

    monkeypatch.setattr(
        public_api,
        "RedisRateLimiter",
        lambda redis: limiter,
    )

    response = client.get(
        "/api/v1/catalog",
        headers={"X-API-Key": TEST_KEY},
    )

    assert response.status_code == 200
    assert response.json()["version"] == "v1"


def test_missing_api_key(monkeypatch) -> None:
    configure_key(
        monkeypatch,
        hashlib.sha256(TEST_KEY.encode()).hexdigest(),
    )

    response = client.get("/api/v1/catalog")
    assert response.status_code == 401


def test_invalid_api_key(monkeypatch) -> None:
    configure_key(
        monkeypatch,
        hashlib.sha256(TEST_KEY.encode()).hexdigest(),
    )

    response = client.get(
        "/api/v1/catalog",
        headers={"X-API-Key": "incorrect"},
    )

    assert response.status_code == 401


def test_unconfigured_api_key(monkeypatch) -> None:
    configure_key(monkeypatch, None)

    response = client.get(
        "/api/v1/catalog",
        headers={"X-API-Key": TEST_KEY},
    )

    assert response.status_code == 503


def test_malformed_hash(monkeypatch) -> None:
    configure_key(monkeypatch, "invalid-hash")

    response = client.get(
        "/api/v1/catalog",
        headers={"X-API-Key": TEST_KEY},
    )

    assert response.status_code == 503


def test_openapi_api_key_security() -> None:
    schema = app.openapi()

    assert "/api/v1/catalog" in schema["paths"]

    schemes = schema["components"]["securitySchemes"]

    assert any(
        scheme.get("type") == "apiKey"
        and scheme.get("in") == "header"
        and scheme.get("name") == "X-API-Key"
        for scheme in schemes.values()
    )

    assert schema["paths"]["/api/v1/catalog"]["get"]["security"]
