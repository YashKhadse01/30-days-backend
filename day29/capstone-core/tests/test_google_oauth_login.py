"""Focused tests for Google OAuth login initiation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from capstone_core.api.google_oauth import (
    GOOGLE_DISCOVERY_URL,
    create_google_oauth_client,
    google_login,
)


def test_google_client_uses_openid_discovery() -> None:
    with patch(
        "capstone_core.api.google_oauth.OAuth"
    ) as mock_oauth_class:
        create_google_oauth_client(
            "test-client-id",
            "test-client-secret",
        )

    mock_oauth_class.return_value.register.assert_called_once_with(
        name="google",
        client_id="test-client-id",
        client_secret="test-client-secret",
        server_metadata_url=GOOGLE_DISCOVERY_URL,
        client_kwargs={"scope": "openid email profile"},
        code_challenge_method="S256",
    )


@pytest.mark.asyncio
async def test_google_login_rejects_missing_configuration() -> None:
    request = MagicMock(spec=Request)

    with patch(
        "capstone_core.api.google_oauth.get_settings"
    ) as mock_settings:
        mock_settings.return_value.google_client_id = None
        mock_settings.return_value.google_client_secret = None
        mock_settings.return_value.oauth_session_secret = None

        with pytest.raises(HTTPException) as error:
            await google_login(request)

    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_google_login_starts_authorization() -> None:
    request = MagicMock(spec=Request)
    expected_response = object()

    mock_client = MagicMock()
    mock_client.google.authorize_redirect = AsyncMock(
        return_value=expected_response
    )

    with (
        patch(
            "capstone_core.api.google_oauth.get_settings"
        ) as mock_settings,
        patch(
            "capstone_core.api.google_oauth.create_google_oauth_client",
            return_value=mock_client,
        ),
    ):
        mock_settings.return_value.google_client_id = "client-id"
        mock_settings.return_value.google_client_secret = "client-secret"
        mock_settings.return_value.oauth_session_secret = "s" * 48
        mock_settings.return_value.google_redirect_uri = (
            "http://127.0.0.1:8765/auth/google/callback"
        )

        response = await google_login(request)

    assert response is expected_response

    mock_client.google.authorize_redirect.assert_awaited_once_with(
        request,
        "http://127.0.0.1:8765/auth/google/callback",
        code_challenge_method="S256",
    )
