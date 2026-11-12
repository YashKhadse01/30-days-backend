
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def create_user(client):
    email = f"status-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    registered = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registered.status_code == 201, registered.text

    logged_in = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert logged_in.status_code == 200, logged_in.text

    return email, {
        "Authorization": (
            f"Bearer {logged_in.json()['access_token']}"
        )
    }


def test_unassigned_member_cannot_update_task_status():
    with TestClient(app) as client:
        _, owner = create_user(client)
        member_email, member = create_user(client)

        organization = client.post(
            "/organizations",
            json={"name": "Task Status Security Team"},
            headers=owner,
        )
        assert organization.status_code == 201, organization.text

        org_id = organization.json()["id"]

        invitation = client.post(
            f"/organizations/{org_id}/invitations",
            json={
                "email": member_email,
                "role": "member",
            },
            headers=owner,
        )
        assert invitation.status_code == 201, invitation.text

        accepted = client.post(
            "/invitations/accept",
            json={
                "token": invitation.json()["invitation_token"],
            },
            headers=member,
        )
        assert accepted.status_code == 200, accepted.text

        tasks_url = f"/organizations/{org_id}/tasks"

        created = client.post(
            tasks_url,
            json={"title": "Protected Task"},
            headers=owner,
        )
        assert created.status_code == 201, created.text

        task_id = created.json()["id"]
        status_url = f"{tasks_url}/{task_id}/status"

        # Unassigned MEMBER cannot update status.
        denied = client.patch(
            status_url,
            json={"status": "done"},
            headers=member,
        )
        assert denied.status_code == 403

        # Task status must remain unchanged.
        unchanged = client.get(
            f"{tasks_url}/{task_id}",
            headers=owner,
        )
        assert unchanged.status_code == 200
        assert unchanged.json()["status"] == "todo"

        # OWNER can update task status.
        updated = client.patch(
            status_url,
            json={"status": "in_progress"},
            headers=owner,
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["status"] == "in_progress"
