
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from multi_tenant_project_api.database import get_db
from multi_tenant_project_api.models import (
    Membership,
    OrganizationRole,
    Task,
    TaskStatus,
    User,
)
from multi_tenant_project_api.routers.auth import get_current_user
from multi_tenant_project_api.schemas.tasks import (
    TaskAssign,
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from multi_tenant_project_api.websocket.manager import (
    connection_manager,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/organizations/{organization_id}/tasks",
    tags=["Tasks"],
)


async def notify_task_change(
    organization_id: str,
    event_type: str,
    task_id: str,
    actor_id: str,
) -> None:
    """Notify connected members of an organization."""
    try:
        await connection_manager.broadcast(
            organization_id,
            {
                "type": event_type,
                "organization_id": organization_id,
                "task_id": task_id,
                "actor_id": actor_id,
            },
        )
    except Exception:
        logger.exception(
            "Failed to broadcast %s for task %s",
            event_type,
            task_id,
        )


async def require_membership(
    db: AsyncSession,
    organization_id: str,
    user_id: str,
) -> Membership:
    membership = await db.scalar(
        select(Membership).where(
            Membership.organization_id == organization_id,
            Membership.user_id == user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    return membership


def require_manager(membership: Membership) -> None:
    if membership.role not in (
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
    ):
        raise HTTPException(
            status_code=403,
            detail="Owner or admin permission required",
        )


async def find_task(
    db: AsyncSession,
    organization_id: str,
    task_id: str,
) -> Task:
    task = await db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.organization_id == organization_id,
        )
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return task


async def validate_assignee(
    db: AsyncSession,
    organization_id: str,
    membership_id: str | None,
) -> None:
    if membership_id is None:
        return

    assignee = await db.scalar(
        select(Membership).where(
            Membership.id == membership_id,
            Membership.organization_id == organization_id,
        )
    )

    if assignee is None:
        raise HTTPException(
            status_code=422,
            detail="Assignee must belong to this organization",
        )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=201,
)
async def create_task(
    organization_id: str,
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = await require_membership(
        db, organization_id, current_user.id
    )
    require_manager(membership)

    await validate_assignee(
        db,
        organization_id,
        payload.assigned_membership_id,
    )

    task = Task(
        organization_id=organization_id,
        title=payload.title,
        description=payload.description,
        assigned_membership_id=payload.assigned_membership_id,
        created_by=current_user.id,
        status=TaskStatus.TODO,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    await notify_task_change(
        organization_id,
        "task.created",
        task.id,
        current_user.id,
    )

    return task


@router.get(
    "",
    response_model=list[TaskResponse],
)
async def list_tasks(
    organization_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_membership(
        db, organization_id, current_user.id
    )

    result = await db.scalars(
        select(Task)
        .where(Task.organization_id == organization_id)
        .order_by(Task.created_at.desc())
    )

    return result.all()


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
async def get_task(
    organization_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_membership(
        db, organization_id, current_user.id
    )

    return await find_task(db, organization_id, task_id)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    organization_id: str,
    task_id: str,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = await require_membership(
        db, organization_id, current_user.id
    )
    require_manager(membership)

    task = await find_task(db, organization_id, task_id)

    updates = payload.model_dump(exclude_unset=True)

    if "title" in updates:
        if updates["title"] is None or not updates["title"].strip():
            raise HTTPException(
                status_code=422,
                detail="Task title cannot be empty",
            )
        task.title = updates["title"]

    if "description" in updates:
        task.description = updates["description"]

    await db.commit()
    await db.refresh(task)

    await notify_task_change(
        organization_id,
        "task.updated",
        task.id,
        current_user.id,
    )

    return task


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse,
)
async def update_task_status(
    organization_id: str,
    task_id: str,
    payload: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = await require_membership(
        db, organization_id, current_user.id
    )

    task = await find_task(db, organization_id, task_id)

    is_manager = membership.role in (
        OrganizationRole.OWNER,
        OrganizationRole.ADMIN,
    )
    is_assignee = (
        task.assigned_membership_id == membership.id
    )

    if not (is_manager or is_assignee):
        raise HTTPException(
            status_code=403,
            detail="Only managers or the assignee can update status",
        )

    task.status = TaskStatus(payload.status.value)

    await db.commit()
    await db.refresh(task)

    await notify_task_change(
        organization_id,
        "task.status_changed",
        task.id,
        current_user.id,
    )

    return task


@router.patch(
    "/{task_id}/assign",
    response_model=TaskResponse,
)
async def assign_task(
    organization_id: str,
    task_id: str,
    payload: TaskAssign,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = await require_membership(
        db, organization_id, current_user.id
    )
    require_manager(membership)

    task = await find_task(db, organization_id, task_id)

    await validate_assignee(
        db,
        organization_id,
        payload.assigned_membership_id,
    )

    task.assigned_membership_id = payload.assigned_membership_id

    await db.commit()
    await db.refresh(task)

    await notify_task_change(
        organization_id,
        "task.assigned",
        task.id,
        current_user.id,
    )

    return task


@router.delete(
    "/{task_id}",
    status_code=204,
)
async def delete_task(
    organization_id: str,
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = await require_membership(
        db, organization_id, current_user.id
    )
    require_manager(membership)

    task = await find_task(db, organization_id, task_id)

    deleted_task_id = task.id

    await db.delete(task)
    await db.commit()

    await notify_task_change(
        organization_id,
        "task.deleted",
        deleted_task_id,
        current_user.id,
    )
