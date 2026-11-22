# Capstone Core ? Advanced Python Backend

Day 29 capstone project from the 30-Day Backend Development roadmap.

A FastAPI backend demonstrating authentication, two-factor verification, Google OAuth, asynchronous services, Redis-backed infrastructure, and secure public API patterns.

## Technology Stack

- Python 3.12+
- FastAPI and Pydantic
- PostgreSQL, SQLAlchemy Async, and Alembic
- Redis caching and rate limiting
- Celery background tasks
- JWT authentication, TOTP 2FA, and Google OAuth
- WebSockets
- pytest, pytest-cov, Ruff, and uv

## Features

- User registration, login, and authenticated profile
- JWT-based authentication
- TOTP two-factor authentication
- Google OAuth integration
- WebSocket echo endpoint
- Celery background task implementation
- Redis JSON caching
- Redis-backed rate limiting
- Versioned public API with API-key authentication
- Redis-backed idempotent demonstration operations
- Signed outgoing webhooks
- Third-party HTTP API integration
- Automatically generated OpenAPI documentation

## Local Setup

1. Install Python 3.12+, uv, and Docker.
2. Copy `.env.example` to `.env`.
3. Replace placeholder secrets and configure local database and Redis URLs.
4. Start the project's PostgreSQL and Redis containers.
5. Install dependencies and apply database migrations:

   ```powershell
   uv sync
   uv run alembic upgrade head
   ```

6. Start the API:

   ```powershell
   uv run uvicorn capstone_core.main:app --reload --port 8765
   ```

7. Open `http://127.0.0.1:8765/docs` for interactive API documentation.

Google OAuth requires credentials from a configured OAuth application. Do not commit `.env` or real credentials.

## Quality Checks

```powershell
uv run ruff check src tests
uv run pytest -q --cov=capstone_core --cov-fail-under=80
```

Latest verified result: **106 passing tests, 87.22% coverage**.

## Technical Documentation

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Security](docs/security.md)
- [Testing](docs/testing.md)

## Scope

This is a learning capstone, not a production-ready payment or enterprise transaction platform. Some integrations are demonstrated through isolated service tests rather than deployed external systems.
