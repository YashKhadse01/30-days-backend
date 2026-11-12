
import uuid

from fastapi.testclient import TestClient

from multi_tenant_project_api.main import app


def create_user_and_login(client):
    email = f"user-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    register = client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201, register.text

    login = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    return {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }


def test_organization_creation_and_tenant_isolation():
    with TestClient(app) as client:
        user_a = create_user_and_login(client)
        user_b = create_user_and_login(client)

        # User A creates an organization
        created = client.post(
            "/organizations",
            json={"name": "Engineering Team"},
            headers=user_a,
        )

        assert created.status_code == 201, created.text
        organization = created.json()
        organization_id = organization["id"]

        # User A can see their organization
        response_a = client.get(
            f"/organizations/{organization_id}",
            headers=user_a,
        )
        assert response_a.status_code == 200

        # User B cannot access User A's organization
        response_b = client.get(
            f"/organizations/{organization_id}",
            headers=user_b,
        )
        assert response_b.status_code == 404

        # User B cannot see User A's organization in listings
        listing_b = client.get(
            "/organizations",
            headers=user_b,
        )
        assert listing_b.status_code == 200
        assert all(
            org["id"] != organization_id
            for org in listing_b.json()
        )

        # Unauthenticated users cannot access organizations
        anonymous = client.get("/organizations")
        assert anonymous.status_code == 401
