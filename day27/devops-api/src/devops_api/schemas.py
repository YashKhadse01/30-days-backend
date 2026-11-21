from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Validate incoming task creation requests."""

    title: str = Field(
        min_length=1,
        max_length=200,
    )


class TaskResponse(BaseModel):
    """Define the public response for a task."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    status: Literal[
        "pending",
        "processing",
        "completed",
        "failed",
    ]
    created_at: datetime
