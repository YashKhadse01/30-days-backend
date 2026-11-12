
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import update

from multi_tenant_project_api.database import AsyncSessionLocal
from multi_tenant_project_api.main import app
from multi_tenant_project_api.models import Invitation


def create_user(client):
    email = f"edge-{uuid.uuid4().hex}@example.com"
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

    return email, {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }


def test_expired_invitation_and_duplicate_membership():
    with TestClient(app) as client:
        _, owner_headers = create_user(client)
        member_email, member_headers = create_user(client)

        created = client.post(
            "/organizations",
            json={"name": "Edge Case Verification Team"},
            headers=owner_headers,
        )
        assert created.status_code == 201, created.text

        organization_id = created.json()["id"]
        invitation_url = (
            f"/organizations/{organization_id}/invitations"
        )

        # Create an invitation
        invited = client.post(
            invitation_url,
            json={"email": member_email, "role": "member"},
            headers=owner_headers,
        )
        assert invited.status_code == 201, invited.text

        invitation_id = invited.json()["id"]
        expired_token = invited.json()["invitation_token"]

        # Expire invitation using the TestClient event loop
        async def expire_invitation():
            async with AsyncSessionLocal() as db:
                await db.execute(
                    update(Invitation)
                    .where(Invitation.id == invitation_id)
                    .values(
                        expires_at=(
                            datetime.now(timezone.utc)
                            - timedelta(hours=1)
                        )
                    )
                )
                await db.commit()

        client.portal.call(expire_invitation)

        # Expired invitation must fail
        expired = client.post(
            "/invitations/accept",
            json={"token": expired_token},
            headers=member_headers,
        )
        assert expired.status_code == 400, expired.text

        # Create a fresh invitation
        fresh = client.post(
            invitation_url,
            json={"email": member_email, "role": "member"},
            headers=owner_headers,
        )
        assert fresh.status_code == 201, fresh.text

        # Accept the fresh invitation
        accepted = client.post(
            "/invitations/accept",
            json={"token": fresh.json()["invitation_token"]},
            headers=member_headers,
        )
        assert accepted.status_code == 200, accepted.text

        # Already-member invitation must be rejected
        duplicate = client.post(
            invitation_url,
            json={"email": member_email, "role": "member"},
            headers=owner_headers,
        )
        assert duplicate.status_code == 409, duplicate.text
