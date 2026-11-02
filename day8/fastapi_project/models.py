from pydantic import BaseModel, Field, ConfigDict

class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str | None = None
    priority: int = Field(default=1, ge=1, le=5)

class TaskResponse(TaskCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    completed: bool = False