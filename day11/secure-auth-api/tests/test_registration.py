import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from secure_auth_api.models import User
from secure_auth_api.security import verify_password
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_register_success(
    client: AsyncClient,
    db_session: AsyncSession,
):
    response = await client.post(
        "/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["is_verified"] is False
    assert isinstance(data["id"], int)
    assert "password" not in data
    assert "password_hash" not in data

    result = await db_session.execute(
        select(User).where(
            User.email == "newuser@example.com"
        )
    )
    user = result.scalar_one()

    assert user.password_hash != "StrongPass123!"
    assert verify_password(
        "StrongPass123!", user.password_hash
    )

@pytest.mark.asyncio
async def test_duplicate_email(client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "StrongPass123!",
    }

    first = await client.post("/auth/register", json=payload)
    second = await client.post("/auth/register", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == (
        "Unable to register with these details"
    )

@pytest.mark.asyncio
async def test_weak_password(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "weak@example.com",
            "password": "weakpassword123!",
        },
    )

    assert response.status_code == 422
    assert "uppercase" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_email_normalization(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "MixedCase@Example.COM",
            "password": "StrongPass123!",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == (
        "mixedcase@example.com"
    )

@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_database_isolation(
    client: AsyncClient,
    db_session: AsyncSession,
):
    result = await db_session.execute(
        select(User).where(
            User.email == "newuser@example.com"
        )
    )

    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_registration_sends_verification_email(client):
    with patch(
        "secure_auth_api.main.send_verification_email"
    ) as mock_send:
        response = await client.post(
            "/auth/register",
            json={
                "email": "email-integration@example.com",
                "password": "StrongPass123!",
            },
        )

    assert response.status_code == 201
    mock_send.assert_called_once()

    email, token = mock_send.call_args.args
    assert email == "email-integration@example.com"
    assert isinstance(token, str)
    assert len(token) >= 32
