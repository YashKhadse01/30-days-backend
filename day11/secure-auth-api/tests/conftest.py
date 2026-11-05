import os
from collections.abc import AsyncIterator
from pathlib import Path
import httpx
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is required")

if make_url(TEST_DATABASE_URL).database != "day11_auth_test":
    raise RuntimeError("Unsafe test database configuration")

from secure_auth_api.database import get_db
from secure_auth_api.main import app
from secure_auth_api.models import Base

@pytest.fixture(scope="session")
def prepare_test_database():
    sync_url = make_url(TEST_DATABASE_URL).set(
        drivername="postgresql+psycopg"
    )
    engine = create_engine(sync_url, poolclass=NullPool)

    try:
        with engine.connect() as connection:
            database_name = connection.scalar(
                text("SELECT current_database()")
            )
            if database_name != "day11_auth_test":
                raise RuntimeError("Unsafe test database")

        Base.metadata.create_all(engine)
        yield
    finally:
        engine.dispose()

@pytest_asyncio.fixture
async def db_session(
    prepare_test_database,
) -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()

            session_factory = async_sessionmaker(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )

            try:
                async with session_factory() as session:
                    yield session
            finally:
                await transaction.rollback()
    finally:
        await engine.dispose()

@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncIterator[httpx.AsyncClient]:

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
