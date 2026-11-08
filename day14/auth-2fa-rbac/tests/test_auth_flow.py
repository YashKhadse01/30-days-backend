
import pytest
from starlette.testclient import TestClient

from auth_2fa_rbac.main import app
from auth_2fa_rbac.auth_service import (
    create_user,
    users,
    sessions,
    login_challenges,
)
from auth_2fa_rbac.totp import (
    generate_totp,
    generate_totp_secret,
)


@pytest.fixture
def auth_client():
    """Create an isolated user for the full login flow."""
    original_users = users.copy()
    original_sessions = sessions.copy()
    original_challenges = login_challenges.copy()

    users.clear()
    sessions.clear()
    login_challenges.clear()

    try:
        secret = generate_totp_secret()

        create_user(
            username="integration_user",
            password="SecureTestPassword123!",
            role="user",
            totp_secret=secret,
        )

        with TestClient(app) as client:
            yield client, secret

    finally:
        users.clear()
        users.update(original_users)

        sessions.clear()
        sessions.update(original_sessions)

        login_challenges.clear()
        login_challenges.update(original_challenges)


def test_complete_authentication_flow(auth_client):
    client, secret = auth_client

    # Step 1: Verify password.
    login_response = client.post(
        "/auth/login",
        json={
            "username": "integration_user",
            "password": "SecureTestPassword123!",
        },
    )

    assert login_response.status_code == 200

    challenge = login_response.json()["challenge_token"]

    # Step 2: Verify authenticator OTP.
    otp = generate_totp(secret)

    verify_response = client.post(
        "/auth/verify-2fa",
        json={
            "challenge_token": challenge,
            "otp": otp,
        },
    )

    assert verify_response.status_code == 200

    session_token = verify_response.json()["session_token"]

    headers = {
        "Authorization": f"Bearer {session_token}"
    }

    # Step 3: Access protected profile.
    profile_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert profile_response.status_code == 200
    assert profile_response.json()["username"] == "integration_user"
    assert profile_response.json()["two_factor_authenticated"] is True

    # Step 4: Access permitted resource.
    reports_response = client.get(
        "/reports",
        headers=headers,
    )

    assert reports_response.status_code == 200

    # Step 5: Reject admin-only resource.
    admin_response = client.get(
        "/admin/users",
        headers=headers,
    )

    assert admin_response.status_code == 403

    # Step 6: Logout.
    logout_response = client.post(
        "/auth/logout",
        headers=headers,
    )

    assert logout_response.status_code == 200

    # Step 7: Reject revoked session.
    revoked_response = client.get(
        "/auth/me",
        headers=headers,
    )

    assert revoked_response.status_code == 401


def test_wrong_password_rejected(auth_client):
    client, _ = auth_client

    response = client.post(
        "/auth/login",
        json={
            "username": "integration_user",
            "password": "IncorrectPassword!",
        },
    )

    assert response.status_code == 401


def test_unknown_user_rejected(auth_client):
    client, _ = auth_client

    response = client.post(
        "/auth/login",
        json={
            "username": "unknown_user",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401


def test_invalid_otp_rejected(auth_client):
    client, secret = auth_client

    login_response = client.post(
        "/auth/login",
        json={
            "username": "integration_user",
            "password": "SecureTestPassword123!",
        },
    )

    assert login_response.status_code == 200

    challenge = login_response.json()["challenge_token"]

    correct_otp = generate_totp(secret)
    invalid_otp = (
        "000000" if correct_otp != "000000" else "999999"
    )

    response = client.post(
        "/auth/verify-2fa",
        json={
            "challenge_token": challenge,
            "otp": invalid_otp,
        },
    )

    assert response.status_code == 401


def test_challenge_cannot_be_reused(auth_client):
    client, secret = auth_client

    login_response = client.post(
        "/auth/login",
        json={
            "username": "integration_user",
            "password": "SecureTestPassword123!",
        },
    )

    challenge = login_response.json()["challenge_token"]
    otp = generate_totp(secret)

    first_response = client.post(
        "/auth/verify-2fa",
        json={
            "challenge_token": challenge,
            "otp": otp,
        },
    )

    assert first_response.status_code == 200

    second_response = client.post(
        "/auth/verify-2fa",
        json={
            "challenge_token": challenge,
            "otp": otp,
        },
    )

    assert second_response.status_code == 401
