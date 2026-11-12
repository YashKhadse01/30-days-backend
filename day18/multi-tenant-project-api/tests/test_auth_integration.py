
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def test_register_login_and_profile():
    email = f"day18-{uuid.uuid4().hex}@example.com"
    password = "SecureDemoPassword123!"

    with TestClient(app) as client:
        # Step 1: Register a new user
        register = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
            },
        )

        assert register.status_code == 201, register.text

        user = register.json()
        assert user["email"] == email
        assert "password_hash" not in user

        # Step 2: Login
        login = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert login.status_code == 200, login.text

        token = login.json()["access_token"]
        assert token

        # Step 3: Access protected profile
        profile = client.get(
            "/auth/me",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert profile.status_code == 200, profile.text
        assert profile.json()["email"] == email

        # Step 4: Reject missing authentication
        unauthorized = client.get("/auth/me")
        assert unauthorized.status_code == 401
