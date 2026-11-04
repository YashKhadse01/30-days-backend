import pytest
from httpx import AsyncClient
from tests.factories import make_task_payload

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    payload = make_task_payload(
        title="Learn Docker",
        description="Practice PostgreSQL with Docker Compose",
    )

    response = await client.post("/tasks", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == payload["title"]
    assert data["description"] == payload["description"]
    assert data["completed"] is False
    assert isinstance(data["id"], int)

@pytest.mark.asyncio
async def test_tasks_are_isolated_between_tests(client: AsyncClient):
    response = await client.get("/tasks")

    assert response.status_code == 200
    assert response.json()["items"] == []

@pytest.mark.asyncio
async def test_get_task(client: AsyncClient):
    payload = make_task_payload(title="Read Task")

    created = await client.post("/tasks", json=payload)
    assert created.status_code == 201

    task_id = created.json()["id"]

    response = await client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Read Task"

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient):
    created = await client.post(
        "/tasks",
        json=make_task_payload(title="Original Task"),
    )
    assert created.status_code == 201

    task_id = created.json()["id"]

    response = await client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "completed": True},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Task"
    assert response.json()["completed"] is True

@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    created = await client.post(
        "/tasks",
        json=make_task_payload(title="Delete Task"),
    )
    assert created.status_code == 201

    task_id = created.json()["id"]

    response = await client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    deleted = await client.get(f"/tasks/{task_id}")
    assert deleted.status_code == 404

@pytest.mark.asyncio
async def test_nonexistent_task_returns_404(client: AsyncClient):
    response = await client.get("/tasks/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_invalid_task_title(client: AsyncClient):
    response = await client.post(
        "/tasks",
        json={"title": "", "description": "Invalid title"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_pagination_limit(client: AsyncClient):
    response = await client.get("/tasks?limit=0")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_cursor_pagination(client: AsyncClient):
    for number in range(5):
        response = await client.post(
            "/tasks",
            json=make_task_payload(title=f"Task {number}"),
        )
        assert response.status_code == 201

    first = await client.get("/tasks?limit=2")

    assert first.status_code == 200
    first_data = first.json()

    assert len(first_data["items"]) == 2
    assert first_data["has_more"] is True
    assert first_data["next_cursor"] is not None

    cursor = first_data["next_cursor"]

    second = await client.get(
        "/tasks",
        params={"cursor": cursor, "limit": 2},
    )

    assert second.status_code == 200
    second_data = second.json()

    assert len(second_data["items"]) == 2

    first_ids = {task["id"] for task in first_data["items"]}
    second_ids = {task["id"] for task in second_data["items"]}

    assert first_ids.isdisjoint(second_ids)


@pytest.mark.asyncio
async def test_update_nonexistent_task(client: AsyncClient):
    response = await client.patch(
        "/tasks/999999999",
        json={"title": "Missing Task"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

@pytest.mark.asyncio
async def test_delete_nonexistent_task(client: AsyncClient):
    response = await client.delete("/tasks/999999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


@pytest.mark.asyncio
async def test_empty_task_list(client: AsyncClient):
    response = await client.get("/tasks")

    assert response.status_code == 200

    data = response.json()

    assert data["items"] == []
    assert data["next_cursor"] is None
    assert data["has_more"] is False


@pytest.mark.asyncio
async def test_invalid_pagination_cursor(client: AsyncClient):
    response = await client.get(
        "/tasks",
        params={"cursor": -1, "limit": 10},
    )

    assert response.status_code == 422

