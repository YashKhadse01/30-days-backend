
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskStatusValue(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskCreate(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )
    assigned_membership_id: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class TaskStatusUpdate(BaseModel):
    status: TaskStatusValue


class TaskAssign(BaseModel):
    assigned_membership_id: str | None


class TaskResponse(BaseModel):
    id: str
    organization_id: str
    title: str
    description: str | None
    status: TaskStatusValue
    assigned_membership_id: str | None
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}
