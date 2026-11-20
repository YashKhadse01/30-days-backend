
import strawberry
from strawberry.types import Info

from graphql_performance_api.auth import require_api_key


@strawberry.type
class Project:
    id: int
    name: str


@strawberry.type
class Task:
    id: int
    title: str
    completed: bool
    project_id: strawberry.Private[int] = 1

    @strawberry.field
    async def project(self, info: Info) -> Project | None:
        loader = info.context["project_loader"]
        data = await loader.load(self.project_id)

        if data is None:
            return None

        return Project(**data)


# Temporary in-memory task data.
TASKS: list[Task] = [
    Task(
        id=1,
        title="Learn Strawberry GraphQL",
        completed=False,
        project_id=1,
    ),
    Task(
        id=2,
        title="Build GraphQL queries",
        completed=False,
        project_id=1,
    ),
    Task(
        id=3,
        title="Test FastAPI integration",
        completed=True,
        project_id=2,
    ),
]


@strawberry.type
class Query:

    @strawberry.field
    def hello(self) -> str:
        return "Welcome to Day 26 GraphQL API!"

    @strawberry.field
    def tasks(self) -> list[Task]:
        return TASKS


@strawberry.type
class Mutation:

    @strawberry.mutation
    def create_task(
        self,
        info: Info,
        title: str,
        project_id: int = 1,
    ) -> Task:
        require_api_key(info)

        cleaned_title = title.strip()

        if not cleaned_title:
            raise ValueError("Task title cannot be empty")

        new_task = Task(
            id=max((task.id for task in TASKS), default=0) + 1,
            title=cleaned_title,
            completed=False,
            project_id=project_id,
        )

        TASKS.append(new_task)
        return new_task

    @strawberry.mutation
    def complete_task(
        self,
        info: Info,
        task_id: int,
    ) -> Task:
        require_api_key(info)

        for task in TASKS:
            if task.id == task_id:
                task.completed = True
                return task

        raise ValueError("Task not found")


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
