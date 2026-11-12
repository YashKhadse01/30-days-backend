
import uuid

import pytest
from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app
from multi_tenant_project_api.websocket.manager import (
    connection_manager,
)


def create_user_and_login(client):
    email = f"notification-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text

    return {
        "Authorization": (
            f"Bearer {response.json()['access_token']}"
        )
    }


def create_organization(client, headers):
    response = client.post(
        "/organizations",
        json={"name": "Notification Test Organization"},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_task(client, organization_id, headers):
    response = client.post(
        f"/organizations/{organization_id}/tasks",
        json={
            "title": "Notification Test Task",
            "description": "Testing real-time notifications",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.parametrize(
    "event_type,action",
    [
        ("task.created", "create"),
        ("task.updated", "update"),
        ("task.status_changed", "status"),
        ("task.assigned", "assign"),
        ("task.deleted", "delete"),
    ],
)
def test_task_notification_events(event_type, action):
    with TestClient(app) as client:
        headers = create_user_and_login(client)
        organization_id = create_organization(client, headers)

        task_id = None

        if action != "create":
            task_id = create_task(
                client, organization_id, headers
            )

        url = f"/ws/organizations/{organization_id}"

        with client.websocket_connect(
            url, headers=headers
        ) as websocket:
            connected = websocket.receive_json()
            assert connected["type"] == "connected"

            base_url = (
                f"/organizations/{organization_id}/tasks"
            )

            if action == "create":
                response = client.post(
                    base_url,
                    json={
                        "title": "Live Task",
                        "description": "WebSocket test",
                    },
                    headers=headers,
                )
                assert response.status_code == 201, response.text
                task_id = response.json()["id"]

            elif action == "update":
                response = client.patch(
                    f"{base_url}/{task_id}",
                    json={"title": "Updated Task"},
                    headers=headers,
                )
                assert response.status_code == 200, response.text

            elif action == "status":
                response = client.patch(
                    f"{base_url}/{task_id}/status",
                    json={"status": "in_progress"},
                    headers=headers,
                )
                assert response.status_code == 200, response.text

            elif action == "assign":
                # The endpoint permits unassigning a task.
                response = client.patch(
                    f"{base_url}/{task_id}/assign",
                    json={"assigned_membership_id": None},
                    headers=headers,
                )
                assert response.status_code == 200, response.text

            elif action == "delete":
                response = client.delete(
                    f"{base_url}/{task_id}",
                    headers=headers,
                )
                assert response.status_code == 204, response.text

            event = websocket.receive_json()

            assert event["type"] == event_type
            assert event["organization_id"] == organization_id
            assert event["task_id"] == task_id
            assert isinstance(event["actor_id"], str)
            assert event["actor_id"]


def test_notifications_are_scoped_to_organization():
    """
    Broadcasting an event to organization A must not
    deliver it to organization B.
    """
    with TestClient(app) as client:
        headers_a = create_user_and_login(client)
        headers_b = create_user_and_login(client)

        organization_a = create_organization(
            client, headers_a
        )
        organization_b = create_organization(
            client, headers_b
        )

        url_a = f"/ws/organizations/{organization_a}"
        url_b = f"/ws/organizations/{organization_b}"

        with client.websocket_connect(
            url_a, headers=headers_a
        ) as websocket_a:
            with client.websocket_connect(
                url_b, headers=headers_b
            ) as websocket_b:
                assert websocket_a.receive_json()["type"] == "connected"
                assert websocket_b.receive_json()["type"] == "connected"

                assert organization_a in connection_manager.connections
                assert organization_b in connection_manager.connections

                task_id = create_task(
                    client, organization_a, headers_a
                )

                event_a = websocket_a.receive_json()

                assert event_a["type"] == "task.created"
                assert event_a["organization_id"] == organization_a
                assert event_a["task_id"] == task_id

                # Organization B's connection is separate.
                assert (
                    connection_manager.connections[organization_a]
                    .isdisjoint(
                        connection_manager.connections[organization_b]
                    )
                )

        assert organization_a not in connection_manager.connections
        assert organization_b not in connection_manager.connections
