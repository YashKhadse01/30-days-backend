"""HTTP-level tests for Google OAuth route registration."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from capstone_core.main import create_app


def test_google_login_route_is_registered() -> None:
    app = create_app()

    schema = app.openapi()

    assert "/auth/google/login" in schema["paths"]
    assert "get" in schema["paths"]["/auth/google/login"]


def test_google_login_returns_503_without_credentials() -> None:
    app = create_app()

    with (
        patch(
            "capstone_core.api.google_oauth.get_settings"
        ) as mock_settings,
        TestClient(app) as client,
    ):
        mock_settings.return_value.google_client_id = None
        mock_settings.return_value.google_client_secret = None
        mock_settings.return_value.oauth_session_secret = None

        response = client.get("/auth/google/login")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Google login is not configured"
    }


def test_health_endpoint_still_works() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
