
from strawberry.dataloader import DataLoader


# Simulated project data.
PROJECTS = {
    1: {"id": 1, "name": "Backend Development"},
    2: {"id": 2, "name": "API Performance"},
}


async def load_projects(
    project_ids: list[int],
) -> list[dict | None]:
    """
    Batch-load projects by ID.

    In a database-backed application, this function
    would execute one SELECT ... WHERE id IN (...)
    query instead of querying each project separately.
    """
    print(f"DataLoader batch: {project_ids}", flush=True)

    return [
        PROJECTS.get(project_id)
        for project_id in project_ids
    ]


def create_project_loader() -> DataLoader:
    """Create a fresh DataLoader for each GraphQL request."""
    return DataLoader(load_fn=load_projects)
