from typing import Annotated

from celery.exceptions import CeleryError
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from devops_api.database import get_db
from devops_api.models import Task
from devops_api.schemas import TaskCreate, TaskResponse
from devops_api.tasks import process_task

DbSession = Annotated[AsyncSession, Depends(get_db)]

app = FastAPI(
    title="Day 27 - DevOps API",
    description=(
        "Containerized FastAPI application with PostgreSQL, Redis, Celery, and Nginx."
    ),
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Basic application health check."""
    return {"status": "healthy"}


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    payload: TaskCreate,
    db: DbSession,
) -> Task:
    """Create a PostgreSQL task and enqueue background processing."""
    task = Task(
        title=payload.title,
        status="pending",
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    try:
        process_task.delay(task.id)
    except (CeleryError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Task saved, but background processing is unavailable",
        ) from exc

    return task


@app.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    db: DbSession,
) -> list[Task]:
    """Retrieve tasks from PostgreSQL."""
    result = await db.execute(select(Task).order_by(Task.id).limit(100))
    return list(result.scalars().all())


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: DbSession,
) -> Task:
    """Retrieve a task by its ID."""
    task = await db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task
