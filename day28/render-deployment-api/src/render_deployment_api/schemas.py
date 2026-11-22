
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TaskStatus = Literal["pending", "completed"]


class TaskCreate(BaseModel):
    """Validate incoming task creation requests."""

    title: str = Field(min_length=1, max_length=200)
    status: TaskStatus = "pending"


class TaskResponse(BaseModel):
    """Represent a task returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: TaskStatus
    created_at: datetime
