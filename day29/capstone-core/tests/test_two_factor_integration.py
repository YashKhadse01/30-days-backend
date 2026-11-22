import uuid
from urllib.parse import parse_qs, urlparse

import httpx
import pyotp
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from capstone_core.core.config import get_settings
from capstone_core.main import app
from capstone_core.models.user import User


@pytest.mark.asyncio
async def test_complete_two_factor_authentication_flow():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    email = f"two-factor-{uuid.uuid4().hex}@example.com"
    password = "IntegrationTestPassword123!"
    user_id = None

    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            register = await client.post(
                "/auth/register",
                json={"email": email, "password": password},
            )
            assert register.status_code == 201, register.text

            user_id = uuid.UUID(register.json()["id"])

            login = await client.post(
                "/auth/login",
                json={"email": email, "password": password},
            )
            assert login.status_code == 200, login.text

            initial_token = login.json()["access_token"]
            headers = {"Authorization": f"Bearer {initial_token}"}

            setup = await client.post(
                "/auth/2fa/setup",
                headers=headers,
            )
            assert setup.status_code == 200, setup.text

            uri = setup.json()["provisioning_uri"]
            secret = parse_qs(urlparse(uri).query)["secret"][0]
            totp = pyotp.TOTP(secret)

            confirm = await client.post(
                "/auth/2fa/confirm",
                headers=headers,
                json={"code": totp.now()},
            )
            assert confirm.status_code == 200, confirm.text
            assert confirm.json()["enabled"] is True

            protected_login = await client.post(
                "/auth/login",
                json={"email": email, "password": password},
            )
            assert protected_login.status_code == 200
            body = protected_login.json()

            assert body["requires_2fa"] is True
            assert "challenge_token" in body
            assert "access_token" not in body

            challenge = body["challenge_token"]

            denied = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {challenge}"},
            )
            assert denied.status_code == 401

            invalid = await client.post(
                "/auth/2fa/verify-login",
                json={
                    "challenge_token": challenge,
                    "code": "abcdef",
                },
            )
            assert invalid.status_code == 422

            # Confirmation consumes the current TOTP time step.
            replay = await client.post(
                "/auth/2fa/verify-login",
                json={
                    "challenge_token": challenge,
                    "code": totp.now(),
                },
            )
            assert replay.status_code == 401

            # Use a different valid time step within the accepted window.
            next_code = totp.at(
                (totp.timecode(__import__("datetime").datetime.now(
                    __import__("datetime").UTC
                )) + 1) * totp.interval
            )

            verified = await client.post(
                "/auth/2fa/verify-login",
                json={
                    "challenge_token": challenge,
                    "code": next_code,
                },
            )
            assert verified.status_code == 200, verified.text

            access_token = verified.json()["access_token"]

            me = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            assert me.status_code == 200
            assert me.json()["email"] == email

            second_replay = await client.post(
                "/auth/2fa/verify-login",
                json={
                    "challenge_token": challenge,
                    "code": next_code,
                },
            )
            assert second_replay.status_code == 401

    finally:
        if user_id is not None:
            async with session_factory() as session:
                await session.execute(
                    delete(User).where(User.id == user_id)
                )
                await session.commit()

        await engine.dispose()
