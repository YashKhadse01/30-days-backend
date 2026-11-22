
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from render_deployment_api.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""


def get_engine() -> Engine:
    """Create a PostgreSQL engine using environment configuration."""
    database_url = get_settings().database_url

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is required for database operations."
        )

    return create_engine(
        database_url,
        pool_pre_ping=True,
    )


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for each API request."""
    engine = get_engine()
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    with session_factory() as session:
        yield session
