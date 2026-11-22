"""Focused tests for Google OAuth callback security."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from capstone_core.api import google_oauth
from capstone_core.models.two_factor import TwoFactorAuth
from capstone_core.models.user import User
from capstone_core.services.google_identity import GoogleEmailConflictError


def make_request() -> Request:
    return Request(
        {"type": "http", "method": "GET", "path": "/auth/google/callback"}
    )


def make_user() -> User:
    return User(
        id=uuid4(),
        email="user@example.com",
        password_hash=None,
        is_active=True,
    )


def configure_oauth(monkeypatch, token: dict) -> None:
    settings = SimpleNamespace(
        google_client_id="test-client",
        google_client_secret="test-secret",
        oauth_session_secret="s" * 40,
        jwt_secret_key="j" * 40,
    )

    monkeypatch.setattr(google_oauth, "get_settings", lambda: settings)

    client = MagicMock()
    client.google.authorize_access_token = AsyncMock(return_value=token)

    monkeypatch.setattr(
        google_oauth,
        "create_google_oauth_client",
        lambda *_args: client,
    )


def verified_token() -> dict:
    return {
        "id_token": "validated-by-authlib",
        "userinfo": {
            "sub": "google-123",
            "email": "user@example.com",
            "email_verified": True,
        },
    }


@pytest.mark.asyncio
async def test_callback_issues_access_token(monkeypatch) -> None:
    configure_oauth(monkeypatch, verified_token())
    user = make_user()

    resolver = AsyncMock(return_value=user)
    monkeypatch.setattr(google_oauth, "resolve_google_user", resolver)

    session = AsyncMock()
    session.get.return_value = None
    response = Response()

    result = await google_oauth.google_callback(
        make_request(), response, session
    )

    assert result.access_token
    assert result.token_type == "bearer"
    assert response.headers["cache-control"] == "no-store"
    resolver.assert_awaited_once()


@pytest.mark.asyncio
async def test_callback_requires_2fa_when_enabled(monkeypatch) -> None:
    configure_oauth(monkeypatch, verified_token())
    user = make_user()

    monkeypatch.setattr(
        google_oauth,
        "resolve_google_user",
        AsyncMock(return_value=user),
    )

    session = AsyncMock()
    session.get.return_value = TwoFactorAuth(
        user_id=user.id,
        encrypted_secret="test",
        is_enabled=True,
    )

    result = await google_oauth.google_callback(
        make_request(), Response(), session
    )

    assert result.challenge_token
    assert not hasattr(result, "access_token")


@pytest.mark.asyncio
async def test_callback_rejects_missing_id_token(monkeypatch) -> None:
    configure_oauth(
        monkeypatch,
        {"userinfo": verified_token()["userinfo"]},
    )

    with pytest.raises(HTTPException) as error:
        await google_oauth.google_callback(
            make_request(), Response(), AsyncMock()
        )

    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_callback_rejects_unverified_email(monkeypatch) -> None:
    token = verified_token()
    token["userinfo"]["email_verified"] = False
    configure_oauth(monkeypatch, token)

    from capstone_core.services.google_identity import (
        GoogleIdentityInvalidError,
    )

    monkeypatch.setattr(
        google_oauth,
        "resolve_google_user",
        AsyncMock(
            side_effect=GoogleIdentityInvalidError("Unverified email")
        ),
    )

    with pytest.raises(HTTPException) as error:
        await google_oauth.google_callback(
            make_request(), Response(), AsyncMock()
        )

    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_callback_prevents_email_account_linking(monkeypatch) -> None:
    configure_oauth(monkeypatch, verified_token())

    monkeypatch.setattr(
        google_oauth,
        "resolve_google_user",
        AsyncMock(
            side_effect=GoogleEmailConflictError("Existing account")
        ),
    )

    with pytest.raises(HTTPException) as error:
        await google_oauth.google_callback(
            make_request(), Response(), AsyncMock()
        )

    assert error.value.status_code == 409
