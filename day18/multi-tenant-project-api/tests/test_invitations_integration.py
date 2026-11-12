
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def create_user(client):
    email = f"invite-{uuid.uuid4().hex}@example.com"
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
        "Authorization": (
            f"Bearer {login.json()['access_token']}"
        )
    }


def test_invitation_workflow():
    with TestClient(app) as client:
        owner_email, owner_headers = create_user(client)
        member_email, member_headers = create_user(client)
        other_email, other_headers = create_user(client)

        # Owner creates an organization
        created = client.post(
            "/organizations",
            json={"name": "Invitation Test Team"},
            headers=owner_headers,
        )
        assert created.status_code == 201, created.text

        organization_id = created.json()["id"]

        # Unauthenticated requests are rejected
        anonymous = client.post(
            f"/organizations/{organization_id}/invitations",
            json={"email": member_email, "role": "member"},
        )
        assert anonymous.status_code == 401

        # Non-member cannot create invitations
        forbidden = client.post(
            f"/organizations/{organization_id}/invitations",
            json={"email": member_email, "role": "member"},
            headers=other_headers,
        )
        assert forbidden.status_code == 403

        # Owner invites the member
        invited = client.post(
            f"/organizations/{organization_id}/invitations",
            json={"email": member_email, "role": "member"},
            headers=owner_headers,
        )
        assert invited.status_code == 201, invited.text

        token = invited.json()["invitation_token"]
        assert token

        # Another user cannot accept the invitation
        wrong_user = client.post(
            "/invitations/accept",
            json={"token": token},
            headers=other_headers,
        )
        assert wrong_user.status_code == 400

        # Invited member accepts
        accepted = client.post(
            "/invitations/accept",
            json={"token": token},
            headers=member_headers,
        )
        assert accepted.status_code == 200, accepted.text
        assert accepted.json()["role"] == "member"

        # Accepted token cannot be reused
        replay = client.post(
            "/invitations/accept",
            json={"token": token},
            headers=member_headers,
        )
        assert replay.status_code == 400

        # New member can access their organization
        accessible = client.get(
            f"/organizations/{organization_id}",
            headers=member_headers,
        )
        assert accessible.status_code == 200

        # Unrelated user remains isolated
        isolated = client.get(
            f"/organizations/{organization_id}",
            headers=other_headers,
        )
        assert isolated.status_code == 404
