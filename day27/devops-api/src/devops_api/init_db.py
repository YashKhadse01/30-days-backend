import asyncio

from devops_api.database import engine
from devops_api.models import Base


async def initialize_database() -> None:
    """Create PostgreSQL tables for the DevOps application."""

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    await engine.dispose()

    print("PostgreSQL tables initialized successfully")


if __name__ == "__main__":
    asyncio.run(initialize_database())
