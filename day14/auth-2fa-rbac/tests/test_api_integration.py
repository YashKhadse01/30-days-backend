
import pytest
from starlette.testclient import TestClient

from auth_2fa_rbac.main import app
from auth_2fa_rbac.auth_service import (
    User,
    sessions,
    users,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def authenticated_client(client):
    """Create isolated sessions for RBAC integration tests."""

    original_users = users.copy()
    original_sessions = sessions.copy()

    users.clear()
    sessions.clear()

    try:
        for role in ("admin", "user", "viewer"):
            users[role] = User(
                username=role,
                password_hash="test-only",
                role=role,
                totp_secret="test-only",
            )

            sessions[f"{role}-test-session"] = (
                role,
                float("inf"),
            )

        yield client

    finally:
        users.clear()
        users.update(original_users)

        sessions.clear()
        sessions.update(original_sessions)


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 200),
        ("user", 200),
        ("viewer", 200),
    ],
)
def test_read_reports(authenticated_client, role, expected):
    response = authenticated_client.get(
        "/reports",
        headers={
            "Authorization": f"Bearer {role}-test-session"
        },
    )

    assert response.status_code == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 200),
        ("user", 200),
        ("viewer", 403),
    ],
)
def test_create_reports(authenticated_client, role, expected):
    response = authenticated_client.post(
        "/reports",
        headers={
            "Authorization": f"Bearer {role}-test-session"
        },
    )

    assert response.status_code == expected


@pytest.mark.parametrize(
    "role,expected",
    [
        ("admin", 200),
        ("user", 403),
        ("viewer", 403),
    ],
)
def test_admin_access(authenticated_client, role, expected):
    response = authenticated_client.get(
        "/admin/users",
        headers={
            "Authorization": f"Bearer {role}-test-session"
        },
    )

    assert response.status_code == expected


@pytest.mark.parametrize(
    "endpoint,method",
    [
        ("/reports", "get"),
        ("/reports", "post"),
        ("/admin/users", "get"),
        ("/auth/me", "get"),
    ],
)
def test_missing_authentication(client, endpoint, method):
    response = getattr(client, method)(endpoint)

    assert response.status_code == 401


def test_invalid_session_rejected(client):
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalid-session-token"
        },
    )

    assert response.status_code == 401


def test_authenticated_profile(authenticated_client):
    response = authenticated_client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer user-test-session"
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "user"
    assert response.json()["two_factor_authenticated"] is True
