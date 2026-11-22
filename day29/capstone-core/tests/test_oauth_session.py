"""Tests for optional OAuth session middleware."""

from unittest.mock import patch

import pytest
from starlette.middleware.sessions import SessionMiddleware

from capstone_core.main import create_app


def test_session_middleware_disabled_without_secret() -> None:
    with patch(
        "capstone_core.main.get_settings"
    ) as mock_settings:
        mock_settings.return_value.oauth_session_secret = None

        app = create_app()

    assert not any(
        middleware.cls is SessionMiddleware
        for middleware in app.user_middleware
    )


def test_session_middleware_enabled_with_valid_secret() -> None:
    with patch(
        "capstone_core.main.get_settings"
    ) as mock_settings:
        mock_settings.return_value.oauth_session_secret = "s" * 48
        mock_settings.return_value.google_redirect_uri = (
            "http://127.0.0.1:8765/auth/google/callback"
        )

        app = create_app()

    assert any(
        middleware.cls is SessionMiddleware
        for middleware in app.user_middleware
    )


def test_short_session_secret_is_rejected() -> None:
    with patch(
        "capstone_core.main.get_settings"
    ) as mock_settings:
        mock_settings.return_value.oauth_session_secret = "short"

        with pytest.raises(ValueError, match="at least 32"):
            create_app()
