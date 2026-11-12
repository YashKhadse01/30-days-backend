
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def create_user(client):
    email = f"crud-{uuid.uuid4().hex}@example.com"
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
        "Authorization": f"Bearer {response.json()['access_token']}"
    }


def create_organization(client, headers):
    response = client.post(
        "/organizations",
        json={"name": "CRUD Coverage Team"},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_task(client, organization_id, headers):
    response = client.post(
        f"/organizations/{organization_id}/tasks",
        json={
            "title": "Initial Task",
            "description": "Initial description",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_task_crud_lifecycle():
    with TestClient(app) as client:
        owner = create_user(client)
        organization_id = create_organization(client, owner)
        task_id = create_task(client, organization_id, owner)

        base_url = f"/organizations/{organization_id}/tasks"

        # List tasks
        response = client.get(base_url, headers=owner)
        assert response.status_code == 200
        assert any(
            task["id"] == task_id for task in response.json()
        )

        # Retrieve a task
        response = client.get(
            f"{base_url}/{task_id}",
            headers=owner,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Initial Task"

        # Update title and description
        response = client.patch(
            f"{base_url}/{task_id}",
            json={
                "title": "Updated Task",
                "description": "Updated description",
            },
            headers=owner,
        )
        assert response.status_code == 200, response.text
        assert response.json()["title"] == "Updated Task"
        assert response.json()["description"] == "Updated description"

        # Update status
        response = client.patch(
            f"{base_url}/{task_id}/status",
            json={"status": "in_progress"},
            headers=owner,
        )
        assert response.status_code == 200, response.text

        # Delete task
        response = client.delete(
            f"{base_url}/{task_id}",
            headers=owner,
        )
        assert response.status_code == 204, response.text

        # Deleted task must not be accessible
        response = client.get(
            f"{base_url}/{task_id}",
            headers=owner,
        )
        assert response.status_code == 404


def test_invalid_task_updates():
    with TestClient(app) as client:
        owner = create_user(client)
        organization_id = create_organization(client, owner)
        task_id = create_task(client, organization_id, owner)

        base_url = f"/organizations/{organization_id}/tasks"

        # Empty task title must be rejected
        response = client.patch(
            f"{base_url}/{task_id}",
            json={"title": ""},
            headers=owner,
        )
        assert response.status_code == 422

        # Nonexistent task must return 404
        response = client.get(
            f"{base_url}/{uuid.uuid4()}",
            headers=owner,
        )
        assert response.status_code == 404

        # Assignment to an unrelated membership must fail
        response = client.patch(
            f"{base_url}/{task_id}/assign",
            json={"assigned_membership_id": str(uuid.uuid4())},
            headers=owner,
        )
        assert response.status_code == 422


def test_cross_tenant_task_access_denied():
    with TestClient(app) as client:
        owner = create_user(client)
        outsider = create_user(client)

        organization_id = create_organization(client, owner)
        task_id = create_task(client, organization_id, owner)

        base_url = f"/organizations/{organization_id}/tasks"

        # Outsider cannot list tasks
        response = client.get(base_url, headers=outsider)
        assert response.status_code == 404

        # Outsider cannot retrieve a task
        response = client.get(
            f"{base_url}/{task_id}",
            headers=outsider,
        )
        assert response.status_code == 404

        # Outsider cannot update a task
        response = client.patch(
            f"{base_url}/{task_id}",
            json={"title": "Unauthorized change"},
            headers=outsider,
        )
        assert response.status_code == 404

        # Outsider cannot delete a task
        response = client.delete(
            f"{base_url}/{task_id}",
            headers=outsider,
        )
        assert response.status_code == 404
