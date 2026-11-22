# Day 30 — Cloud Deployment Report

## Objective

Deploy the Day 29 FastAPI capstone to a public HTTPS endpoint
using Docker, Render, Neon PostgreSQL, and Upstash Redis.

## Deployment Architecture

```text
                   HTTPS Client
                        |
                        v
                Render Web Service
                capstone-core-api
                        |
                  Docker Container
                        |
                   FastAPI / Uvicorn
                        |
              +---------+---------+
              |                   |
              v                   v
       Neon PostgreSQL      Upstash Redis
       Singapore region     Singapore region
              |                   |
       SQLAlchemy Async      API-key rate limits
       Alembic migrations    Cache / Idempotency
```

## Infrastructure

| Component | Configuration |
|---|---|
| Application | FastAPI |
| Runtime | Python 3.12 |
| Packaging | uv |
| Container | Docker |
| Hosting | Render Free |
| Database | Neon PostgreSQL 16 |
| Cache | Upstash Redis with TLS |
| Transport | HTTPS |
| Region | Singapore |

## Deployment Process

1. Prepared the capstone Dockerfile for Render.
2. Configured a Render Docker web service.
3. Provisioned a Neon PostgreSQL database.
4. Provisioned an Upstash Redis instance.
5. Configured application environment variables in Render.
6. Applied Alembic migrations to Neon.
7. Verified application health and API integration.
8. Pushed security hardening to GitHub.
9. Confirmed the updated commit deployed successfully.

## Runtime Configuration

The deployed application uses:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `TOTP_ENCRYPTION_KEY`
- `API_KEY_SHA256`
- `PORT=10000`

Actual credentials are not stored in this document.

The PostgreSQL connection uses the asyncpg driver with TLS.
The Redis connection uses a TLS-enabled `rediss://` URL.

## Database Migration

Migrations were applied using:

```powershell
uv run alembic upgrade head
```

Verified migration revision: `e7ff44976ed1`.

Verified tables include:

- `users`
- `two_factor_auth`
- `oauth_identities`
- `alembic_version`

## Live Endpoints

- Health: https://capstone-core-api.onrender.com/health
- Swagger: https://capstone-core-api.onrender.com/docs
- OpenAPI: https://capstone-core-api.onrender.com/openapi.json

## Verified Application Workflows

- Live health endpoint returned HTTP 200.
- User registration persisted data to Neon.
- Login issued a JWT access token.
- Authenticated `/auth/me` returned the user profile.
- Redis-backed public API-key authentication worked.
- Idempotent operation creation and replay worked.
- Conflicting idempotency payload returned HTTP 409.

## GitHub Deployment Evidence

Docker deployment preparation commit: `1b43693`.

Security hardening commit: `c705d0a`.

Render confirmed the security-hardening commit as live on
November 22, 2026.

## Limitations

- Render Free may sleep after inactivity.
- Google OAuth is implemented but not configured for live login.
- A dedicated cloud Celery worker has not been deployed.
- Production monitoring and operational alerting are not verified.
- The deployment is a learning demonstration, not a production SLA.
