
import asyncio

import pytest

from graphql_performance_api.dataloaders import (
    create_project_loader,
)


@pytest.mark.asyncio
async def test_dataloader_batches_requests(monkeypatch):
    """Multiple IDs should be fetched in one batch."""

    from graphql_performance_api import dataloaders

    batches = []

    async def tracked_load(project_ids):
        batches.append(list(project_ids))
        return [
            dataloaders.PROJECTS.get(project_id)
            for project_id in project_ids
        ]

    monkeypatch.setattr(
        dataloaders,
        "load_projects",
        tracked_load,
    )

    loader = create_project_loader()

    results = await asyncio.gather(
        loader.load(1),
        loader.load(2),
        loader.load(1),
    )

    assert len(batches) == 1
    assert batches[0] == [1, 2]

    assert results[0]["name"] == "Backend Development"
    assert results[1]["name"] == "API Performance"
    assert results[2]["name"] == "Backend Development"


@pytest.mark.asyncio
async def test_dataloader_caches_repeated_keys(monkeypatch):
    """Repeated loads should use the loader cache."""

    from graphql_performance_api import dataloaders

    call_count = 0

    async def tracked_load(project_ids):
        nonlocal call_count
        call_count += 1

        return [
            dataloaders.PROJECTS.get(project_id)
            for project_id in project_ids
        ]

    monkeypatch.setattr(
        dataloaders,
        "load_projects",
        tracked_load,
    )

    loader = create_project_loader()

    first = await loader.load(1)
    second = await loader.load(1)

    assert first == second
    assert call_count == 1


@pytest.mark.asyncio
async def test_missing_project_returns_none():
    """Unknown project IDs should return None."""

    loader = create_project_loader()

    result = await loader.load(999)

    assert result is None
