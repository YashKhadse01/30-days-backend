import os
import pytest
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from collections.abc import AsyncIterator
from sqlalchemy.pool import NullPool
import httpx
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from testing_docker_api.database import get_db
from testing_docker_api.main import app
from testing_docker_api.models import Base
PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(
    dotenv_path=PROJECT_ROOT / ".env",
    override=False,
)

@pytest.fixture(scope="session")
def prepare_test_database():
    test_url = os.environ.get("TEST_DATABASE_URL")

    if not test_url:
        raise RuntimeError("TEST_DATABASE_URL is required")

    sync_url = make_url(test_url).set(
        drivername="postgresql+psycopg"
    )

    sync_engine = create_engine(sync_url, poolclass=NullPool)

    try:
        with sync_engine.connect() as conn:
            name = conn.scalar(text("SELECT current_database()"))

        if name != "day10_tasks_test":
            raise RuntimeError(f"Unsafe test database: {name!r}")

        Base.metadata.create_all(sync_engine)

    finally:
        sync_engine.dispose()

@pytest_asyncio.fixture
async def test_engine(prepare_test_database):
    test_url = os.environ.get("TEST_DATABASE_URL")

    engine = create_async_engine(
        test_url,
        echo=False,
        poolclass=NullPool,
    )

    try:
        yield engine
    finally:
        await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncIterator[AsyncSession]:
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            async with session_factory() as session:
                yield session
        finally:
            await transaction.rollback()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            yield test_client

    finally:
        app.dependency_overrides.pop(get_db, None)
