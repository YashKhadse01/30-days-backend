
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from multi_tenant_project_api.database import AsyncSessionLocal
from multi_tenant_project_api.main import app
from multi_tenant_project_api.models import Membership


def create_user(client):
    email = f"task-rbac-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    response = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    user_id = response.json()["id"]

    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text

    return email, user_id, {
        "Authorization": f"Bearer {response.json()['access_token']}"
    }


def invite_member(
    client, org_id, inviter_headers,
    email, member_headers, role
):
    response = client.post(
        f"/organizations/{org_id}/invitations",
        json={"email": email, "role": role},
        headers=inviter_headers,
    )
    assert response.status_code == 201, response.text

    accepted = client.post(
        "/invitations/accept",
        json={"token": response.json()["invitation_token"]},
        headers=member_headers,
    )
    assert accepted.status_code == 200, accepted.text


def test_task_role_permissions_and_assignment():
    with TestClient(app) as client:
        _, _, owner = create_user(client)
        admin_email, _, admin = create_user(client)
        member_email, member_id, member = create_user(client)
        _, _, outsider = create_user(client)

        org = client.post(
            "/organizations",
            json={"name": "Task Permissions Team"},
            headers=owner,
        )
        assert org.status_code == 201, org.text
        org_id = org.json()["id"]

        invite_member(
            client, org_id, owner,
            admin_email, admin, "admin",
        )
        invite_member(
            client, org_id, admin,
            member_email, member, "member",
        )

        tasks_url = f"/organizations/{org_id}/tasks"

        # MEMBER cannot create tasks
        denied = client.post(
            tasks_url,
            json={"title": "Unauthorized Task"},
            headers=member,
        )
        assert denied.status_code == 403

        # ADMIN can create tasks
        created = client.post(
            tasks_url,
            json={"title": "Implement WebSockets"},
            headers=admin,
        )
        assert created.status_code == 201, created.text
        task_id = created.json()["id"]

        # Find member's organization membership
        async def find_member_membership():
            async with AsyncSessionLocal() as db:
                return await db.scalar(
                    select(Membership.id).where(
                        Membership.organization_id == org_id,
                        Membership.user_id == member_id,
                    )
                )

        membership_id = client.portal.call(
            find_member_membership
        )
        assert membership_id is not None

        # ADMIN assigns task to MEMBER
        assigned = client.patch(
            f"{tasks_url}/{task_id}/assign",
            json={"assigned_membership_id": membership_id},
            headers=admin,
        )
        assert assigned.status_code == 200, assigned.text

        # Assigned MEMBER can update task status
        updated = client.patch(
            f"{tasks_url}/{task_id}/status",
            json={"status": "in_progress"},
            headers=member,
        )
        assert updated.status_code == 200, updated.text
        assert updated.json()["status"] == "in_progress"

        # MEMBER cannot delete tasks
        denied_delete = client.delete(
            f"{tasks_url}/{task_id}",
            headers=member,
        )
        assert denied_delete.status_code == 403

        # Outsider cannot access tasks
        outsider_response = client.get(
            f"{tasks_url}/{task_id}",
            headers=outsider,
        )
        assert outsider_response.status_code == 404

        # OWNER can delete tasks
        deleted = client.delete(
            f"{tasks_url}/{task_id}",
            headers=owner,
        )
        assert deleted.status_code == 204
