
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from render_deployment_api.config import get_settings
from render_deployment_api.database import get_db
from render_deployment_api.models import Task
from render_deployment_api.schemas import TaskCreate, TaskResponse

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Day 28 - Cloud Deployment and Capstone Design",
    version="0.1.0",
)

DbSession = Annotated[Session, Depends(get_db)]


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to Day 28 Render Deployment API",
        "environment": settings.app_env,
    }


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(payload: TaskCreate, db: DbSession) -> Task:
    """Create and persist a task."""
    task = Task(
        title=payload.title,
        status=payload.status,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(db: DbSession) -> list[Task]:
    """Retrieve all tasks."""
    return list(db.scalars(select(Task).order_by(Task.id)).all())


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: DbSession) -> Task:
    """Retrieve a task by its ID."""
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task
