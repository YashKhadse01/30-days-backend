import uuid

from httpx import ASGITransport, AsyncClient

from session_auth_api.csrf import CSRF_COOKIE_NAME
from session_auth_api.database import settings
from session_auth_api.main import app
import pytest
from sqlalchemy import text


@pytest.mark.asyncio
async def test_database_connection(db_session):
    result = await db_session.execute(
        text("SELECT current_database()")
    )

    database_name = result.scalar_one()

    assert database_name == "day12_auth_test"


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_login_rotation_revokes_old_session(client):
    # Register a unique user in the isolated test database.
    email = f"rotation-{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    registration = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201, registration.text

    credentials = {
        "email": email,
        "password": password,
    }

    # First login creates session A.
    first_login = await client.post(
        "/auth/login",
        json=credentials,
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    assert first_login.status_code == 200, first_login.text

    session_a = client.cookies.get(
        settings.session_cookie_name
    )
    csrf_a = client.cookies.get(CSRF_COOKIE_NAME)

    assert session_a
    assert csrf_a

    # Second login rotates session A into session B.
    second_login = await client.post(
        "/auth/login",
        json=credentials,
         headers={
        "Origin": "http://127.0.0.1:8000",
        "X-CSRF-Token": csrf_a,
         },   
    )
    assert second_login.status_code == 200, second_login.text

    session_b = client.cookies.get(
        settings.session_cookie_name
    )

    assert session_b
    assert session_a != session_b

    # Session B must remain authenticated.
    current_session = await client.get("/auth/me")
    assert current_session.status_code == 200
    assert current_session.json()["email"] == email

    # Use a separate client to replay the old session A.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000",
    ) as old_client:
        old_client.cookies.set(
            settings.session_cookie_name,
            session_a,
        )

        old_session = await old_client.get("/auth/me")

    # Session A must no longer authenticate.
    assert old_session.status_code == 401

@pytest.mark.asyncio
async def test_logout_all_revokes_multiple_devices(client):
    email = f"devices-{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"
    origin = {"Origin": "http://127.0.0.1:8000"}

    registration = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201, registration.text

    credentials = {"email": email, "password": password}

    # Device A logs in.
    login_a = await client.post(
        "/auth/login",
        json=credentials,
        headers=origin,
    )
    assert login_a.status_code == 200, login_a.text

    csrf_a = client.cookies.get(CSRF_COOKIE_NAME)
    assert csrf_a

    # Device B uses a separate cookie jar.
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://127.0.0.1:8000",
    ) as device_b:
        login_b = await device_b.post(
            "/auth/login",
            json=credentials,
            headers=origin,
        )
        assert login_b.status_code == 200, login_b.text

        # Both devices should be authenticated.
        assert (await client.get("/auth/me")).status_code == 200
        assert (await device_b.get("/auth/me")).status_code == 200

        # Device A logs out of all devices.
        logout = await client.post(
            "/auth/logout-all",
            headers={
                **origin,
                "X-CSRF-Token": csrf_a,
            },
        )
        assert logout.status_code == 200, logout.text

        # Both sessions must now be rejected.
        assert (await client.get("/auth/me")).status_code == 401
        assert (await device_b.get("/auth/me")).status_code == 401

@pytest.mark.asyncio
async def test_untrusted_origin_rejected(client):
    email = f"origin-{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    registration = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201, registration.text

    credentials = {"email": email, "password": password}

    # An untrusted website must not initiate login.
    blocked_login = await client.post(
        "/auth/login",
        json=credentials,
        headers={"Origin": "https://evil.example"},
    )

    assert blocked_login.status_code == 403

    # A trusted origin can log in.
    valid_login = await client.post(
        "/auth/login",
        json=credentials,
        headers={"Origin": "http://127.0.0.1:8000"},
    )
    assert valid_login.status_code == 200, valid_login.text

    csrf_token = client.cookies.get(CSRF_COOKIE_NAME)
    assert csrf_token

    # Even with a valid CSRF token, an untrusted
    # origin must not be allowed to log out.
    blocked_logout = await client.post(
        "/auth/logout",
        headers={
            "Origin": "https://evil.example",
            "X-CSRF-Token": csrf_token,
        },
    )

    assert blocked_logout.status_code == 403

    # The rejected logout must preserve the session.
    profile = await client.get("/auth/me")
    assert profile.status_code == 200

@pytest.mark.asyncio
async def test_logout_rejects_missing_and_invalid_csrf(client):
    email = f"csrf-{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"
    origin = {"Origin": "http://127.0.0.1:8000"}

    registration = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201, registration.text

    login = await client.post(
        "/auth/login",
        json={"email": email, "password": password},
        headers=origin,
    )
    assert login.status_code == 200, login.text

    csrf_token = client.cookies.get(CSRF_COOKIE_NAME)
    assert csrf_token

    # Case 1: Missing CSRF header.
    missing = await client.post(
        "/auth/logout",
        headers=origin,
    )
    assert missing.status_code == 403

    # Case 2: Invalid CSRF header.
    invalid = await client.post(
        "/auth/logout",
        headers={
            **origin,
            "X-CSRF-Token": "invalid-csrf-token",
        },
    )
    assert invalid.status_code == 403

    # Neither rejected request should revoke the session.
    profile = await client.get("/auth/me")
    assert profile.status_code == 200

    # Case 3: Valid CSRF header.
    valid = await client.post(
        "/auth/logout",
        headers={
            **origin,
            "X-CSRF-Token": csrf_token,
        },
    )
    assert valid.status_code == 200, valid.text

    # Logout must invalidate the session.
    after_logout = await client.get("/auth/me")
    assert after_logout.status_code == 401

@pytest.mark.asyncio
async def test_login_rejects_missing_origin(client):
    email = f"missing-origin-{uuid.uuid4().hex}@example.com"
    password = "StrongPass123!"

    registration = await client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201, registration.text

    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
        headers={
            "Origin": "",
            "Referer": "",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] in {
        "Missing request origin",
        "Untrusted request origin",
    }
