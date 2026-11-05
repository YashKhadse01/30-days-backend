
from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from secure_auth_api.models import User, EmailVerificationToken
from secure_auth_api.tokens import (
    generate_verification_token,
    hash_verification_token,
)


async def create_verification_user(
    db_session: AsyncSession,
    email: str,
    expired: bool = False,
):
    raw_token = generate_verification_token()

    user = User(
        email=email,
        password_hash="test-only-hash",
        is_verified=False,
    )

    db_session.add(user)
    await db_session.flush()

    expiry = datetime.now(timezone.utc) + timedelta(
        minutes=-1 if expired else 30
    )

    verification = EmailVerificationToken(
        user_id=user.id,
        token_hash=hash_verification_token(raw_token),
        expires_at=expiry,
    )

    db_session.add(verification)
    await db_session.flush()

    return user.id, raw_token


@pytest.mark.asyncio
async def test_verify_email_success(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_id, token = await create_verification_user(
        db_session, "verify@example.com"
    )

    response = await client.post(
        "/auth/verify-email",
        json={"token": token},
    )

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Email verified successfully"
    )

    db_session.expire_all()
    user = await db_session.get(User, user_id)
    assert user.is_verified is True


@pytest.mark.asyncio
async def test_invalid_token(client: AsyncClient):
    response = await client.post(
        "/auth/verify-email",
        json={"token": "invalid-token"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Invalid or expired verification token"
    )


@pytest.mark.asyncio
async def test_expired_token(
    client: AsyncClient,
    db_session: AsyncSession,
):
    user_id, token = await create_verification_user(
        db_session,
        "expired@example.com",
        expired=True,
    )

    response = await client.post(
        "/auth/verify-email",
        json={"token": token},
    )

    assert response.status_code == 400

    db_session.expire_all()
    user = await db_session.get(User, user_id)
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_token_cannot_be_reused(
    client: AsyncClient,
    db_session: AsyncSession,
):
    _, token = await create_verification_user(
        db_session, "reuse@example.com"
    )

    first = await client.post(
        "/auth/verify-email",
        json={"token": token},
    )

    second = await client.post(
        "/auth/verify-email",
        json={"token": token},
    )

    assert first.status_code == 200
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_token_marked_as_used(
    client: AsyncClient,
    db_session: AsyncSession,
):
    _, token = await create_verification_user(
        db_session, "used@example.com"
    )

    response = await client.post(
        "/auth/verify-email",
        json={"token": token},
    )

    assert response.status_code == 200

    db_session.expire_all()

    result = await db_session.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash
            == hash_verification_token(token)
        )
    )

    verification = result.scalar_one()
    assert verification.used_at is not None
