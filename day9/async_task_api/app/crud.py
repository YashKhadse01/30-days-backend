from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate

async def create_task(
    db: AsyncSession,
    data: TaskCreate,
) -> Task:
    task = Task(**data.model_dump())

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task

async def get_task(
    db: AsyncSession,
    task_id: int,
) -> Task | None:
    return await db.get(Task, task_id)

async def get_tasks(
    db: AsyncSession,
    cursor: int | None = None,
    limit: int = 10,
) -> tuple[list[Task], int | None, bool]:
    query = select(Task).order_by(Task.id.asc())

    if cursor is not None:
        query = query.where(Task.id > cursor)

    # Fetch one extra row to determine whether
    # another page exists.
    query = query.limit(limit + 1)

    result = await db.execute(query)
    rows = list(result.scalars().all())

    has_more = len(rows) > limit
    tasks = rows[:limit]

    next_cursor = (
        tasks[-1].id if has_more and tasks else None
    )

    return tasks, next_cursor, has_more

async def update_task(
    db: AsyncSession,
    task_id: int,
    data: TaskUpdate,
) -> Task | None:
    task = await db.get(Task, task_id)

    if task is None:
        return None

    updates = data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    return task

async def delete_task(
    db: AsyncSession,
    task_id: int,
) -> bool:
    task = await db.get(Task, task_id)

    if task is None:
        return False

    await db.delete(task)
    await db.commit()

    return True