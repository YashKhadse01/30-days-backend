
import uuid

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from multi_tenant_project_api.main import app
from multi_tenant_project_api.websocket.manager import (
    connection_manager,
)


def create_user_and_login(client):
    """Register a user and return JWT authorization headers."""
    email = f"ws-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    register = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert register.status_code == 201, register.text

    login = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def create_organization(client, headers):
    """Create an organization owned by the authenticated user."""
    response = client.post(
        "/organizations",
        json={"name": "WebSocket Test Organization"},
        headers=headers,
    )

    assert response.status_code == 201, response.text

    return response.json()["id"]


def test_valid_member_can_connect():
    """An organization member can establish a WebSocket connection."""
    with TestClient(app) as client:
        headers = create_user_and_login(client)
        organization_id = create_organization(client, headers)

        url = f"/ws/organizations/{organization_id}"

        with client.websocket_connect(
            url,
            headers=headers,
        ) as websocket:
            message = websocket.receive_json()

            assert message["type"] == "connected"
            assert message["organization_id"] == organization_id

            assert organization_id in connection_manager.connections
            assert len(
                connection_manager.connections[organization_id]
            ) == 1

        assert organization_id not in connection_manager.connections


def test_cross_tenant_websocket_rejected():
    """A user cannot subscribe to another organization's events."""
    with TestClient(app) as client:
        user_a = create_user_and_login(client)
        user_b = create_user_and_login(client)

        organization_id = create_organization(client, user_a)

        url = f"/ws/organizations/{organization_id}"

        try:
            with client.websocket_connect(
                url,
                headers=user_b,
            ) as websocket:
                websocket.receive_json()

        except WebSocketDisconnect as exc:
            assert exc.code == 1008

        else:
            raise AssertionError(
                "Cross-tenant WebSocket access was allowed"
            )


def test_invalid_jwt_rejected():
    """A malformed JWT must not authorize a WebSocket connection."""
    with TestClient(app) as client:
        url = f"/ws/organizations/{uuid.uuid4()}"

        try:
            with client.websocket_connect(
                url,
                headers={
                    "Authorization": "Bearer invalid.jwt.token"
                },
            ) as websocket:
                websocket.receive_json()

        except WebSocketDisconnect as exc:
            assert exc.code == 1008

        else:
            raise AssertionError(
                "Invalid JWT was accepted"
            )


def test_missing_jwt_rejected():
    """Connections without authorization must be rejected."""
    with TestClient(app) as client:
        url = f"/ws/organizations/{uuid.uuid4()}"

        try:
            with client.websocket_connect(url) as websocket:
                websocket.receive_json()

        except WebSocketDisconnect as exc:
            assert exc.code == 1008

        else:
            raise AssertionError(
                "Unauthenticated WebSocket access was allowed"
            )
