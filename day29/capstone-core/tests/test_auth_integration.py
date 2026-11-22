import asyncio
import uuid

import httpx
from sqlalchemy import delete

from capstone_core.db.session import AsyncSessionLocal
from capstone_core.main import app
from capstone_core.models.user import User


async def run_auth_integration() -> None:
    email = f"capstone-test-{uuid.uuid4().hex}@example.com"
    password = "SecureTestPassword123!"
    user_id = None

    try:
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            registration = await client.post(
                "/auth/register",
                json={
                    "email": email.upper(),
                    "password": password,
                },
            )
            assert registration.status_code == 201, registration.text

            profile = registration.json()
            user_id = uuid.UUID(profile["id"])
            assert profile["email"] == email
            assert "password_hash" not in profile
            print("PASS: Registration")

            duplicate = await client.post(
                "/auth/register",
                json={"email": email, "password": password},
            )
            assert duplicate.status_code == 409, duplicate.text
            print("PASS: Duplicate email rejected")

            login = await client.post(
                "/auth/login",
                json={"email": email.upper(), "password": password},
            )
            assert login.status_code == 200, login.text

            token = login.json()["access_token"]
            assert token
            print("PASS: Login and JWT issuance")

            invalid_login = await client.post(
                "/auth/login",
                json={"email": email, "password": "WrongPassword123!"},
            )
            assert invalid_login.status_code == 401
            print("PASS: Invalid password rejected")

            authenticated = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert authenticated.status_code == 200, authenticated.text
            assert authenticated.json()["id"] == str(user_id)
            print("PASS: Protected profile access")

            invalid_token = await client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid-token"},
            )
            assert invalid_token.status_code == 401
            print("PASS: Invalid JWT rejected")

            missing_token = await client.get("/auth/me")
            assert missing_token.status_code in (401, 403)
            print("PASS: Missing JWT rejected")

    finally:
        if user_id is not None:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    delete(User).where(User.id == user_id)
                )
                await session.commit()
            print("PASS: Test account cleaned up")


def test_authentication_database_flow() -> None:
    asyncio.run(run_auth_integration())
