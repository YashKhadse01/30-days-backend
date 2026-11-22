import uuid

import httpx
import pytest
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from capstone_core.auth.security import create_access_token
from capstone_core.core.config import get_settings
from capstone_core.main import app
from capstone_core.models.user import User


@pytest.mark.asyncio
async def test_authentication_rejects_invalid_credentials_and_tokens():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    email = f"negative-auth-{uuid.uuid4().hex}@example.com"
    password = "ValidTestPassword123!"
    user_id = None

    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            missing_user = await client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert missing_user.status_code == 401

            registered = await client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert registered.status_code == 201, registered.text
            user_id = uuid.UUID(registered.json()["id"])

            duplicate = await client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert duplicate.status_code == 409

            wrong_password = await client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": "IncorrectPassword123!",
                },
            )
            assert wrong_password.status_code == 401

            invalid_token = await client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid.jwt.token"},
            )
            assert invalid_token.status_code == 401

            nonexistent_token = create_access_token(
                subject=str(uuid.uuid4()),
                secret_key=settings.jwt_secret_key,
            )

            nonexistent_user = await client.get(
                "/auth/me",
                headers={
                    "Authorization": f"Bearer {nonexistent_token}"
                },
            )
            assert nonexistent_user.status_code == 401

            async with session_factory() as session:
                await session.execute(
                    update(User)
                    .where(User.id == user_id)
                    .values(is_active=False)
                )
                await session.commit()

            inactive_login = await client.post(
                "/auth/login",
                json={
                    "email": email,
                    "password": password,
                },
            )
            assert inactive_login.status_code == 401

            inactive_token = create_access_token(
                subject=str(user_id),
                secret_key=settings.jwt_secret_key,
            )

            inactive_user = await client.get(
                "/auth/me",
                headers={
                    "Authorization": f"Bearer {inactive_token}"
                },
            )
            assert inactive_user.status_code == 401

    finally:
        if user_id is not None:
            async with session_factory() as session:
                await session.execute(
                    delete(User).where(User.id == user_id)
                )
                await session.commit()

        await engine.dispose()
