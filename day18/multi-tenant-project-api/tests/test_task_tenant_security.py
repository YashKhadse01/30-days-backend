
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from multi_tenant_project_api.database import AsyncSessionLocal
from multi_tenant_project_api.main import app
from multi_tenant_project_api.models import Membership


def create_user(client):
    email = f"tenant-{uuid.uuid4().hex}@example.com"
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

    return registered.json()["id"], {
        "Authorization": (
            f"Bearer {login.json()['access_token']}"
        )
    }


def test_cross_tenant_assignment_is_rejected():
    with TestClient(app) as client:
        user_a_id, user_a = create_user(client)
        user_b_id, user_b = create_user(client)

        org_a = client.post(
            "/organizations",
            json={"name": "Organization Alpha"},
            headers=user_a,
        )
        assert org_a.status_code == 201, org_a.text

        org_b = client.post(
            "/organizations",
            json={"name": "Organization Beta"},
            headers=user_b,
        )
        assert org_b.status_code == 201, org_b.text

        org_a_id = org_a.json()["id"]
        org_b_id = org_b.json()["id"]

        # Retrieve Organization B's membership ID.
        async def get_other_membership():
            async with AsyncSessionLocal() as db:
                return await db.scalar(
                    select(Membership.id).where(
                        Membership.organization_id == org_b_id,
                        Membership.user_id == user_b_id,
                    )
                )

        other_membership_id = client.portal.call(
            get_other_membership
        )
        assert other_membership_id is not None

        tasks_url = f"/organizations/{org_a_id}/tasks"

        # Reject cross-tenant assignment during creation.
        invalid_creation = client.post(
            tasks_url,
            json={
                "title": "Cross-Tenant Task",
                "assigned_membership_id": other_membership_id,
            },
            headers=user_a,
        )
        assert invalid_creation.status_code == 422

        # Create a valid task.
        created = client.post(
            tasks_url,
            json={"title": "Secure Task"},
            headers=user_a,
        )
        assert created.status_code == 201, created.text

        task_id = created.json()["id"]

        # Reject cross-tenant reassignment.
        invalid_assignment = client.patch(
            f"{tasks_url}/{task_id}/assign",
            json={
                "assigned_membership_id": other_membership_id,
            },
            headers=user_a,
        )
        assert invalid_assignment.status_code == 422

        # Verify the task remains unassigned.
        task = client.get(
            f"{tasks_url}/{task_id}",
            headers=user_a,
        )
        assert task.status_code == 200
        assert task.json()["assigned_membership_id"] is None

        # Organization B cannot access Organization A's task.
        unauthorized = client.get(
            f"{tasks_url}/{task_id}",
            headers=user_b,
        )
        assert unauthorized.status_code == 404
