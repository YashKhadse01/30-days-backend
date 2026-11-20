
import pytest
from httpx import ASGITransport, AsyncClient

from graphql_performance_api.auth import settings
from graphql_performance_api.main import app
from graphql_performance_api.schema import TASKS


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def restore_tasks():
    """Restore in-memory tasks after each test."""
    original = [
        (task.id, task.title, task.completed, task.project_id)
        for task in TASKS
    ]

    yield

    TASKS.clear()

    from graphql_performance_api.schema import Task

    TASKS.extend(
        Task(
            id=task_id,
            title=title,
            completed=completed,
            project_id=project_id,
        )
        for task_id, title, completed, project_id in original
    )


@pytest.mark.anyio
async def test_health_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.anyio
async def test_public_graphql_query():
    query = """
    query {
        hello
        tasks {
            id
            title
            project {
                name
            }
        }
    }
    """

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/graphql",
            json={"query": query},
        )

    assert response.status_code == 200

    body = response.json()

    assert "errors" not in body
    assert body["data"]["hello"] == (
        "Welcome to Day 26 GraphQL API!"
    )
    assert len(body["data"]["tasks"]) >= 3


@pytest.mark.anyio
async def test_unauthorized_mutation():
    mutation = """
    mutation {
        createTask(title: "Unauthorized test") {
            id
        }
    }
    """

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/graphql",
            json={"query": mutation},
        )

    body = response.json()

    assert response.status_code == 200
    assert body["data"] is None
    assert body["errors"][0]["message"] == "Unauthorized"


@pytest.mark.anyio
async def test_authorized_mutation():
    mutation = """
    mutation {
        createTask(title: "Automated test task") {
            id
            title
            completed
        }
    }
    """

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/graphql",
            headers={
                "X-API-Key": settings.graphql_api_key,
            },
            json={"query": mutation},
        )

    body = response.json()

    assert response.status_code == 200
    assert "errors" not in body

    task = body["data"]["createTask"]

    assert task["title"] == "Automated test task"
    assert task["completed"] is False
