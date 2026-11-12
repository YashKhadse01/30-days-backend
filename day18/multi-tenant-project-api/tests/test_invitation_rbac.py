
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def create_user(client):
    email = f"rbac-{uuid.uuid4().hex}@example.com"
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

    return email, {
        "Authorization": (
            f"Bearer {response.json()['access_token']}"
        )
    }


def invite_and_accept(
    client, organization_id,
    inviter_headers, email, invitee_headers, role
):
    response = client.post(
        f"/organizations/{organization_id}/invitations",
        json={"email": email, "role": role},
        headers=inviter_headers,
    )
    assert response.status_code == 201, response.text

    token = response.json()["invitation_token"]

    response = client.post(
        "/invitations/accept",
        json={"token": token},
        headers=invitee_headers,
    )
    assert response.status_code == 200, response.text


def test_organization_role_permissions():
    with TestClient(app) as client:
        _, owner_headers = create_user(client)
        admin_email, admin_headers = create_user(client)
        member_email, member_headers = create_user(client)
        outsider_email, outsider_headers = create_user(client)

        created = client.post(
            "/organizations",
            json={"name": "RBAC Verification Team"},
            headers=owner_headers,
        )
        assert created.status_code == 201, created.text

        organization_id = created.json()["id"]

        # OWNER invites ADMIN
        invite_and_accept(
            client, organization_id,
            owner_headers, admin_email,
            admin_headers, "admin",
        )

        # ADMIN invites MEMBER
        invite_and_accept(
            client, organization_id,
            admin_headers, member_email,
            member_headers, "member",
        )

        # MEMBER cannot create invitations
        forbidden = client.post(
            f"/organizations/{organization_id}/invitations",
            json={
                "email": outsider_email,
                "role": "member",
            },
            headers=member_headers,
        )
        assert forbidden.status_code == 403

        # Outsider cannot create invitations
        outsider = client.post(
            f"/organizations/{organization_id}/invitations",
            json={
                "email": outsider_email,
                "role": "member",
            },
            headers=outsider_headers,
        )
        assert outsider.status_code == 403

        # OWNER, ADMIN, and MEMBER can access organization
        for headers in (
            owner_headers,
            admin_headers,
            member_headers,
        ):
            response = client.get(
                f"/organizations/{organization_id}",
                headers=headers,
            )
            assert response.status_code == 200

        # Outsider cannot access organization
        response = client.get(
            f"/organizations/{organization_id}",
            headers=outsider_headers,
        )
        assert response.status_code == 404
