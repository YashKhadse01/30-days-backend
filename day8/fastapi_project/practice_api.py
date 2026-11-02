from fastapi import FastAPI, HTTPException, status
from models import TaskCreate, TaskResponse
from fastapi import Query

app = FastAPI(
    title="Day 8 Backend API",
    description="FastAPI fundamentals and API design",
    version="1.0.0",
)

tasks: dict[int, TaskResponse] = {}
next_id = 1

@app.get("/")
def home():
    return {"message": "Welcome to Day 8 FastAPI"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task: TaskCreate):
    global next_id

    new_task = TaskResponse(
        id=next_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        completed=False,
    )

    tasks[next_id] = new_task
    next_id += 1

    return new_task

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    return list(tasks.values())

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return tasks[task_id]

@app.get("/search", response_model=list[TaskResponse])
def search_tasks(
    keyword: str | None = Query(default=None, min_length=2),
    priority: int | None = Query(default=None, ge=1, le=5),
):
    results = list(tasks.values())

    if keyword is not None:
        results = [
            task for task in results
            if keyword.lower() in task.title.lower()
        ]

    if priority is not None:
        results = [
            task for task in results
            if task.priority == priority
        ]

    return results

@app.get("/search", response_model=list[TaskResponse])
def search_tasks(
    keyword: str | None = Query(default=None, min_length=2),
    priority: int | None = Query(default=None, ge=1, le=5),
):
    results = list(tasks.values())

    if keyword is not None:
        results = [
            task for task in results
            if keyword.lower() in task.title.lower()
        ]

    if priority is not None:
        results = [
            task for task in results
            if task.priority == priority
        ]

    return results