
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from multi_tenant_project_api.database import AsyncSessionLocal
from multi_tenant_project_api.main import app
from multi_tenant_project_api.models import (
    Membership,
    OrganizationRole,
)


def test_organization_creator_becomes_owner():
    email = f"owner-{uuid.uuid4().hex}@example.com"
    password = "SecurePassword123!"

    with TestClient(app) as client:
        # Register user
        registered = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": password,
            },
        )
        assert registered.status_code == 201, registered.text

        user_id = registered.json()["id"]

        # Login
        login = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )
        assert login.status_code == 200, login.text

        token = login.json()["access_token"]

        # Create organization
        created = client.post(
            "/organizations",
            json={"name": "Owner Verification Team"},
            headers={
                "Authorization": f"Bearer {token}",
            },
        )
        assert created.status_code == 201, created.text

        organization_id = created.json()["id"]

        # Query membership on the TestClient event loop
        async def verify_membership():
            async with AsyncSessionLocal() as db:
                membership = await db.scalar(
                    select(Membership).where(
                        Membership.organization_id
                        == organization_id,
                        Membership.user_id == user_id,
                    )
                )

                assert membership is not None
                assert membership.role == OrganizationRole.OWNER

        client.portal.call(verify_membership)
