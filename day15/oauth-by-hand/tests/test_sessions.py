
import time

import pytest
from fastapi.testclient import TestClient

from oauth_by_hand.main import app
from oauth_by_hand.account_linking import (
    create_local_user,
    users,
    google_accounts,
)
from oauth_by_hand.sessions import (
    create_session,
    get_session_user_id,
    revoke_session,
    sessions,
)


# -------------------------
# Test fixtures
# -------------------------

@pytest.fixture(autouse=True)
def reset_data():
    users.clear()
    google_accounts.clear()
    sessions.clear()

    yield

    users.clear()
    google_accounts.clear()
    sessions.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# -------------------------
# Session management tests
# -------------------------

def test_session_creation():
    token = create_session("user-123")

    assert len(token) == 43
    assert get_session_user_id(token) == "user-123"


def test_invalid_session_rejected():
    assert get_session_user_id("invalid-token") is None


def test_expired_session_rejected():
    token = create_session("user-123")
    sessions[token].expires_at = time.time() - 1

    assert get_session_user_id(token) is None
    assert token not in sessions


def test_session_revocation():
    token = create_session("user-123")

    revoke_session(token)

    assert get_session_user_id(token) is None


# -------------------------
# Authentication tests
# -------------------------

def test_profile_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_profile_with_valid_session(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    client.cookies.set("app_session", token)

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["user_id"] == user.user_id
    assert response.json()["email"] == "user@example.com"


def test_profile_with_invalid_session(client):
    client.cookies.set("app_session", "invalid-token")

    response = client.get("/auth/me")

    assert response.status_code == 401


def test_unknown_user_session_rejected(client):
    token = create_session("deleted-user")

    client.cookies.set("app_session", token)

    response = client.get("/auth/me")

    assert response.status_code == 401


# -------------------------
# Cookie-based logout tests
# -------------------------

def test_logout_revokes_session(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    client.cookies.set("app_session", token)

    response = client.post(
        "/auth/logout",
        headers={
            "Origin": "http://testserver",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
    assert get_session_user_id(token) is None

    profile = client.get("/auth/me")
    assert profile.status_code == 401


def test_cross_origin_logout_rejected(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    client.cookies.set("app_session", token)

    response = client.post(
        "/auth/logout",
        headers={
            "Origin": "https://attacker.example",
        },
    )

    assert response.status_code == 403
    assert get_session_user_id(token) == user.user_id


def test_logout_without_origin_rejected(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    client.cookies.set("app_session", token)

    response = client.post(
        "/auth/logout",
    )

    assert response.status_code == 403
    assert get_session_user_id(token) == user.user_id


def test_logout_with_valid_referer(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    client.cookies.set("app_session", token)

    response = client.post(
        "/auth/logout",
        headers={
            "Referer": "http://testserver/dashboard",
        },
    )

    assert response.status_code == 200
    assert get_session_user_id(token) is None


def test_logout_with_invalid_referer(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    client.cookies.set("app_session", token)

    response = client.post(
        "/auth/logout",
        headers={
            "Referer": "https://attacker.example/dashboard",
        },
    )

    assert response.status_code == 403
    assert get_session_user_id(token) == user.user_id


# -------------------------
# Bearer token tests
# -------------------------

def test_bearer_token_authentication(client):
    user = create_local_user("user@example.com")
    token = create_session(user.user_id)

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == user.user_id


def test_bearer_logout_revokes_session(client):
    user = create_local_user("bearer@example.com")
    token = create_session(user.user_id)

    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert get_session_user_id(token) is None

    profile = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert profile.status_code == 401
