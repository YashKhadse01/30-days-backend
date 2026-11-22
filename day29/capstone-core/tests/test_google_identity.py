"""Tests for Google identity resolution and transaction handling."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from capstone_core.models.oauth_identity import OAuthIdentity
from capstone_core.models.user import User
from capstone_core.services.google_identity import (
    GoogleEmailConflictError,
    GoogleIdentityInactiveError,
    GoogleIdentityInvalidError,
    resolve_google_user,
)


def make_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()

    # AsyncSession.execute() is awaited, but its Result is synchronous.
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    return session


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("subject", "email", "verified"),
    [
        ("", "user@example.com", True),
        ("google-123", "", True),
        ("google-123", "user@example.com", False),
    ],
)
async def test_invalid_google_identity_rejected(
    subject: str,
    email: str,
    verified: bool,
) -> None:
    session = make_session()

    with pytest.raises(GoogleIdentityInvalidError):
        await resolve_google_user(
            session,
            subject=subject,
            email=email,
            email_verified=verified,
        )

    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_existing_google_identity_resolves_user() -> None:
    session = make_session()
    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash=None,
        is_active=True,
    )
    identity = OAuthIdentity(
        user_id=user.id,
        provider="google",
        provider_subject="google-123",
    )

    session.execute.return_value.scalar_one_or_none.return_value = identity
    session.get.return_value = user

    resolved = await resolve_google_user(
        session,
        subject="google-123",
        email="user@example.com",
        email_verified=True,
    )

    assert resolved is user
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_inactive_google_user_rejected() -> None:
    session = make_session()
    user = User(
        id=uuid4(),
        email="user@example.com",
        password_hash=None,
        is_active=False,
    )
    identity = OAuthIdentity(
        user_id=user.id,
        provider="google",
        provider_subject="google-123",
    )

    session.execute.return_value.scalar_one_or_none.return_value = identity
    session.get.return_value = user

    with pytest.raises(GoogleIdentityInactiveError):
        await resolve_google_user(
            session,
            subject="google-123",
            email="user@example.com",
            email_verified=True,
        )


@pytest.mark.asyncio
async def test_existing_email_is_not_automatically_linked() -> None:
    session = make_session()

    first_result = MagicMock()
    first_result.scalar_one_or_none.return_value = None

    second_result = MagicMock()
    second_result.scalar_one_or_none.return_value = User(
        id=uuid4(),
        email="user@example.com",
        password_hash="existing-password-hash",
        is_active=True,
    )

    session.execute.side_effect = [first_result, second_result]

    with pytest.raises(GoogleEmailConflictError):
        await resolve_google_user(
            session,
            subject="google-123",
            email="user@example.com",
            email_verified=True,
        )

    session.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_stage", ["flush", "commit"])
async def test_integrity_error_rolls_back(
    failure_stage: str,
) -> None:
    session = make_session()
    session.execute.return_value.scalar_one_or_none.return_value = None

    error = IntegrityError(
        statement="INSERT",
        params={},
        orig=Exception("unique constraint"),
    )

    getattr(session, failure_stage).side_effect = error

    with pytest.raises(GoogleEmailConflictError):
        await resolve_google_user(
            session,
            subject="google-123",
            email="user@example.com",
            email_verified=True,
        )

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_new_google_user_created_without_password() -> None:
    session = make_session()
    session.execute.return_value.scalar_one_or_none.return_value = None

    user = await resolve_google_user(
        session,
        subject="google-123",
        email="  USER@Example.com  ",
        email_verified=True,
    )

    assert user.email == "user@example.com"
    assert user.password_hash is None
    assert user.is_active is True

    added = [call.args[0] for call in session.add.call_args_list]

    assert any(isinstance(item, User) for item in added)
    assert any(
        isinstance(item, OAuthIdentity)
        and item.provider_subject == "google-123"
        for item in added
    )

    session.flush.assert_awaited_once()
    session.commit.assert_awaited_once()
