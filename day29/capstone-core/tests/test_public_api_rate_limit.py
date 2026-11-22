"""HTTP tests for public API rate limiting."""

import hashlib
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from capstone_core.api import public_api
from capstone_core.main import app

client = TestClient(app)
TEST_KEY = "rate-limit-test-key"


def configure(monkeypatch, allowed: bool) -> AsyncMock:
    settings = SimpleNamespace(
        api_key_sha256=hashlib.sha256(
            TEST_KEY.encode()
        ).hexdigest(),
        redis_url="redis://localhost:6379/0",
    )

    monkeypatch.setattr(
        public_api,
        "get_settings",
        lambda: settings,
    )

    limiter = AsyncMock()
    limiter.allow.return_value = allowed

    monkeypatch.setattr(
        public_api,
        "RedisRateLimiter",
        lambda redis: limiter,
    )

    redis = AsyncMock()
    monkeypatch.setattr(
        public_api.Redis,
        "from_url",
        lambda url: redis,
    )

    return limiter


def test_request_allowed(monkeypatch) -> None:
    limiter = configure(monkeypatch, True)

    response = client.get(
        "/api/v1/catalog",
        headers={"X-API-Key": TEST_KEY},
    )

    assert response.status_code == 200
    limiter.allow.assert_awaited_once()


def test_rate_limit_exceeded(monkeypatch) -> None:
    configure(monkeypatch, False)

    response = client.get(
        "/api/v1/catalog",
        headers={"X-API-Key": TEST_KEY},
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"


def test_missing_key_rejected_before_redis(monkeypatch) -> None:
    limiter = configure(monkeypatch, True)

    response = client.get("/api/v1/catalog")

    assert response.status_code == 401
    limiter.allow.assert_not_awaited()
