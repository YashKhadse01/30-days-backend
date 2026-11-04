from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from testing_docker_api import crud
from testing_docker_api.database import engine, get_db
from testing_docker_api.models import Base
from testing_docker_api.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskPage

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Create missing tables for our learning project.
    # Production projects should use Alembic migrations.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(
    title="Day 9 â€” Async Task API",
    description="Async PostgreSQL CRUD with cursor-based pagination",
    version="1.0.0",
    lifespan=lifespan,
)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    return await crud.create_task(db, data)

@app.get("/tasks", response_model=TaskPage)
async def list_tasks(
    cursor: int | None = Query(default=None, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    tasks, next_cursor, has_more = await crud.get_tasks(
        db,
        cursor=cursor,
        limit=limit,
    )

    return TaskPage(
        items=tasks,
        next_cursor=next_cursor,
        has_more=has_more,
    )

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    task = await crud.get_task(db, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    task = await crud.update_task(db, task_id, data)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task

@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await crud.delete_task(db, task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

