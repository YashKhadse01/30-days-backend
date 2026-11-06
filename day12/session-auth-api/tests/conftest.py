
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from session_auth_api.database import get_db, settings
from session_auth_api.main import app
from session_auth_api.models import Base


@pytest_asyncio.fixture
async def db_session():
    """Provide an isolated database transaction for each test."""

    dev_url = make_url(settings.database_url)
    test_url = make_url(settings.test_database_url)

    if (
        dev_url.render_as_string(hide_password=False)
        == test_url.render_as_string(hide_password=False)
        or dev_url.database == test_url.database
    ):
        raise RuntimeError(
            "Test database must be separate from development database"
        )

    engine = create_async_engine(
        settings.test_database_url,
        echo=False,
    )

    try:
        async with engine.begin() as connection:
            # Create missing tables in the test database.
            await connection.run_sync(Base.metadata.create_all)

        async with engine.connect() as connection:
            transaction = await connection.begin()

            session_factory = async_sessionmaker(
                bind=connection,
                class_=AsyncSession,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )

            async with session_factory() as session:
                yield session

            # Roll back changes made during the test.
            await transaction.rollback()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session):
    """Create an HTTP client using the isolated test session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://127.0.0.1:8000",
        ) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
