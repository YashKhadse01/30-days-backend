
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def create_user(client):
    email = f"task-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    registered = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registered.status_code == 201, registered.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    return {
        "Authorization": (
            f"Bearer {login.json()['access_token']}"
        )
    }


def test_task_creation_and_tenant_isolation():
    with TestClient(app) as client:
        owner_headers = create_user(client)
        outsider_headers = create_user(client)

        # Create organization
        created_org = client.post(
            "/organizations",
            json={"name": "Task Integration Team"},
            headers=owner_headers,
        )
        assert created_org.status_code == 201, created_org.text

        organization_id = created_org.json()["id"]
        tasks_url = f"/organizations/{organization_id}/tasks"

        # Owner creates task
        created_task = client.post(
            tasks_url,
            json={
                "title": "Build Project API",
                "description": "Implement task management",
            },
            headers=owner_headers,
        )
        assert created_task.status_code == 201, created_task.text

        task = created_task.json()
        task_id = task["id"]

        assert task["title"] == "Build Project API"
        assert task["status"] == "todo"
        assert task["organization_id"] == organization_id

        # Owner lists tasks
        listing = client.get(
            tasks_url,
            headers=owner_headers,
        )
        assert listing.status_code == 200
        assert any(
            item["id"] == task_id
            for item in listing.json()
        )

        # Owner retrieves task
        retrieved = client.get(
            f"{tasks_url}/{task_id}",
            headers=owner_headers,
        )
        assert retrieved.status_code == 200

        # Outsider cannot list tasks
        outsider_listing = client.get(
            tasks_url,
            headers=outsider_headers,
        )
        assert outsider_listing.status_code == 404

        # Outsider cannot retrieve task
        outsider_task = client.get(
            f"{tasks_url}/{task_id}",
            headers=outsider_headers,
        )
        assert outsider_task.status_code == 404

        # Unauthenticated requests are rejected
        anonymous = client.get(tasks_url)
        assert anonymous.status_code == 401
