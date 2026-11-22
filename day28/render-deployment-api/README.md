
# Day 28 — FastAPI Render Deployment

A production-oriented FastAPI demonstration deployed on Render with PostgreSQL, Alembic migrations, HTTPS, and database backup verification.

## Live Application

- API: https://day28-fastapi-api.onrender.com/
- Health check: https://day28-fastapi-api.onrender.com/health
- Swagger UI: https://day28-fastapi-api.onrender.com/docs

## Technology Stack

- Python 3.12
- FastAPI and Uvicorn
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic Settings
- uv
- pytest
- Render

## Implemented Features

- REST API for task creation and retrieval
- PostgreSQL persistence
- Environment-based configuration
- Alembic database migrations
- HTTPS deployment on Render
- Automated health endpoint tests
- PostgreSQL backup and recovery verification

## Local Development

Install dependencies:

```bash
uv sync
```

Configure environment variables using `.env.example` as a reference. Never commit `.env`.

Run database migrations:

```bash
uv run alembic upgrade head
```

Start the API:

```bash
uv run uvicorn render_deployment_api.main:app --reload
```

Run tests:

```bash
uv run pytest -v
```

## Render Deployment

| Setting | Value |
|---|---|
| Runtime | Python 3 |
| Root Directory | day28/render-deployment-api |
| Build Command | bash scripts/build.sh |
| Start Command | bash scripts/start.sh |
| Region | Singapore |
| Database | Render PostgreSQL |

Production environment variables:

- `APP_ENV=production`
- `DATABASE_URL` — PostgreSQL connection string using the psycopg driver
- `APP_SECRET_KEY` — Secure random secret

Credentials must be configured in Render, not committed to GitHub.

The startup script applies Alembic migrations before starting Uvicorn. This approach is intended for the current single-instance demonstration.

## Database Backup and Recovery

A Render PostgreSQL backup was created using `pg_dump` in custom format.

The backup was:

1. Stored outside the Git repository.
2. Inspected using `pg_restore --list`.
3. Converted into a separate SQL file for compatibility testing.
4. Restored into an isolated local PostgreSQL database.
5. Verified by querying the recovered task record.

The original backup archive was preserved.

### Compatibility Note

The Render PostgreSQL 18.7 backup contained `pg_attver` statements not recognized by the local PostgreSQL 18.6 server.

For the restore test, those statements were removed from a separate SQL copy. The original `.dump` file was not modified.

Backups must be stored securely and restoration should be tested regularly.

Render's free PostgreSQL database expires after 30 days.

## Capstone Design

The proposed Task & Project Management API is documented separately.

See [Capstone Design](docs/capstone-design.md).

The design includes:

- PostgreSQL schema
- REST API specification
- Mermaid architecture diagram
- Authentication and authorization
- Security and deployment strategy

The full capstone is a design proposal and is not implemented in this Day 28 application.

## Security

- Secrets are supplied through environment variables.
- `.env` and `.venv` are excluded from Git.
- HTTPS protects public API traffic.
- Database credentials are not stored in source control.
- Database backups are stored outside the repository.
