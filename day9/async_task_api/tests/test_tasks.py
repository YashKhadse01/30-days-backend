import os
from collections.abc import AsyncIterator
from urllib.parse import urlsplit
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.database import get_db
from app.main import app
from app.models import Base

def get_test_database_url() -> str:
    from dotenv import load_dotenv

    load_dotenv()

    url = os.getenv("TEST_DATABASE_URL")

    if not url:
        raise RuntimeError(
            "TEST_DATABASE_URL is missing from .env"
        )

    parsed = urlsplit(url)

    if (
        parsed.scheme != "postgresql+asyncpg"
        or parsed.path != "/day9_tasks_test"
    ):
        raise RuntimeError(
            "Tests must use the day9_tasks_test database"
        )

    return url

@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    test_engine = create_async_engine(
        get_test_database_url(),
        pool_pre_ping=True,
    )

    session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    try:
        async with test_engine.begin() as connection:
            database_name = await connection.scalar(
                text("SELECT current_database()")
            )

            if database_name != "day9_tasks_test":
                raise RuntimeError(
                    "Refusing to modify a non-test database"
                )

            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

        app.dependency_overrides[get_db] = override_get_db

        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client

    finally:
        app.dependency_overrides.clear()
        await test_engine.dispose()

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_create_task(client):
    response = await client.post(
        "/tasks",
        json={
            "title": "Learn async testing",
            "description": "Test PostgreSQL integration",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] > 0
    assert data["title"] == "Learn async testing"
    assert data["completed"] is False
    assert "created_at" in data

@pytest.mark.asyncio
async def test_get_task(client):
    created = await client.post(
        "/tasks",
        json={"title": "Read task"},
    )

    task_id = created.json()["id"]

    response = await client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Read task"

@pytest.mark.asyncio
async def test_update_task(client):
    created = await client.post(
        "/tasks",
        json={"title": "Original task"},
    )

    task_id = created.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Updated task",
            "completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated task"
    assert response.json()["completed"] is True

@pytest.mark.asyncio
async def test_delete_task(client):
    created = await client.post(
        "/tasks",
        json={"title": "Delete this task"},
    )

    task_id = created.json()["id"]

    deleted = await client.delete(f"/tasks/{task_id}")

    assert deleted.status_code == 204

    missing = await client.get(f"/tasks/{task_id}")

    assert missing.status_code == 404

@pytest.mark.asyncio
async def test_missing_task(client):
    response = await client.get("/tasks/999999")

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_invalid_title(client):
    response = await client.post(
        "/tasks",
        json={"title": "Hi"},
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_cursor_pagination(client):
    for number in range(1, 6):
        response = await client.post(
            "/tasks",
            json={"title": f"Pagination task {number}"},
        )
        assert response.status_code == 201

    first = await client.get("/tasks?limit=2")

    assert first.status_code == 200

    first_data = first.json()

    assert len(first_data["items"]) == 2
    assert first_data["has_more"] is True
    assert first_data["next_cursor"] is not None

    second = await client.get(
        "/tasks",
        params={
            "limit": 2,
            "cursor": first_data["next_cursor"],
        },
    )

    second_data = second.json()

    assert len(second_data["items"]) == 2
    assert second_data["has_more"] is True

    first_ids = {
        item["id"] for item in first_data["items"]
    }

    second_ids = {
        item["id"] for item in second_data["items"]
    }

    assert first_ids.isdisjoint(second_ids)

    third = await client.get(
        "/tasks",
        params={
            "limit": 2,
            "cursor": second_data["next_cursor"],
        },
    )

    third_data = third.json()

    assert len(third_data["items"]) == 1
    assert third_data["has_more"] is False
    assert third_data["next_cursor"] is None

@pytest.mark.asyncio
async def test_invalid_page_limit(client):
    response = await client.get("/tasks?limit=101")

    assert response.status_code == 422
