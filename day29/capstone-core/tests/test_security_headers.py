"""Regression tests for HTTP security headers."""

from fastapi.testclient import TestClient

from capstone_core.main import app


def test_health_endpoint_security_headers() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
