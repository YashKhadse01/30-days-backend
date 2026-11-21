# Day 27 — DevOps API

A containerized FastAPI application demonstrating production-oriented backend deployment practices, asynchronous task processing, automated testing, and continuous integration.

Part of the **30 Days of Backend Development** journey.

## Overview

This project demonstrates how multiple backend services work together in a Docker-based environment.

It combines FastAPI, PostgreSQL, Redis, Celery, Gunicorn, Uvicorn, and Nginx to create a task-processing API with persistent storage and asynchronous background execution.

The project also includes automated code-quality checks, static type checking, API tests, and a GitHub Actions CI workflow.

## Technology Stack

| Technology     | Purpose                                  |
| -------------- | ---------------------------------------- |
| Python 3.12    | Application language                     |
| FastAPI        | REST API framework                       |
| PostgreSQL 16  | Relational database                      |
| SQLAlchemy     | Database ORM                             |
| Redis 7        | Celery message broker and result backend |
| Celery         | Background task processing               |
| Gunicorn       | Application process management           |
| Uvicorn        | ASGI worker implementation               |
| Nginx          | Reverse proxy                            |
| Docker         | Application containerization             |
| Docker Compose | Multi-service orchestration              |
| uv             | Python dependency management             |
| Ruff           | Linting and formatting                   |
| mypy           | Static type checking                     |
| pytest         | Automated testing                        |
| GitHub Actions | Continuous integration                   |

## System Architecture

```text
                    HTTP Request
                         |
                         v
                  +-------------+
                  |    Nginx    |
                  | Port 8081   |
                  +-------------+
                         |
                         v
                 +----------------+
                 |    FastAPI     |
                 | Gunicorn +     |
                 | Uvicorn        |
                 +----------------+
                    |          |
                    v          v
              +----------+  +----------+
              |PostgreSQL|  |  Redis   |
              | Database |  |  Broker  |
              +----------+  +----------+
                                  |
                                  v
                            +-----------+
                            |  Celery   |
                            |  Worker   |
                            +-----------+
                                  |
                                  v
                            +-----------+
                            |PostgreSQL |
                            |Task Status|
                            +-----------+
```

### Request Processing

1. A client sends an HTTP request to Nginx.
2. Nginx forwards the request to the FastAPI application.
3. FastAPI validates the request and stores task information in PostgreSQL.
4. FastAPI publishes a background task through Celery using Redis.
5. A Celery worker processes the task.
6. The worker updates the task status in PostgreSQL.
7. Clients can retrieve task information using the REST API.

## Project Structure

```text
day27/
└── devops-api/
    ├── src/
    │   └── devops_api/
    │       ├── __init__.py
    │       ├── main.py
    │       ├── config.py
    │       ├── database.py
    │       ├── models.py
    │       ├── schemas.py
    │       ├── celery_app.py
    │       ├── tasks.py
    │       └── init_db.py
    ├── tests/
    │   ├── test_health.py
    │   └── test_tasks.py
    ├── nginx/
    │   └── nginx.conf
    ├── Dockerfile
    ├── compose.yaml
    ├── .dockerignore
    ├── .env.example
    ├── .python-version
    ├── pyproject.toml
    ├── uv.lock
    └── README.md
```

The CI workflow is stored at the Git repository root:

```text
.github/workflows/day27-ci.yml
```

## Features

### REST API

- Health-check endpoint
- Task creation with request validation
- Task listing
- Task retrieval by ID
- HTTP error handling

### Background Processing

- Celery task queue
- Redis message broker
- PostgreSQL-backed task status
- Background task execution
- Handling of task-dispatch failures

### Containerization

- Multi-stage Docker build
- Non-root application container
- Docker Compose service orchestration
- Persistent PostgreSQL and Redis volumes
- Container health checks
- Nginx reverse proxy

### Code Quality

- Ruff linting
- Ruff formatting
- mypy static type checking
- pytest automated tests
- GitHub Actions CI workflow

## Prerequisites

Install the following tools:

- Docker Desktop with Docker Compose
- Python 3.12
- uv
- Git

Docker Desktop must be running before starting the containers.

## Environment Configuration

Create a local `.env` file using `.env.example` as the reference.

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the environment variables required by the application.

| Variable              | Purpose                                           |
| --------------------- | ------------------------------------------------- |
| `APP_NAME`            | Application name                                  |
| `APP_ENV`             | Application environment                           |
| `POSTGRES_PASSWORD`   | PostgreSQL password                               |
| `DATABASE_URL_DOCKER` | PostgreSQL connection URL used by Docker services |
| `DATABASE_URL`        | PostgreSQL connection URL for local execution     |
| `REDIS_URL`           | Redis connection URL                              |

Use a strong password and ensure the PostgreSQL password matches the password embedded in the database connection URL.

For Docker services, use the Compose service hostname `postgres` rather than `localhost`.

**Security:** Never commit `.env`, passwords, tokens, or private credentials to Git.

The `.env.example` file should contain placeholders or non-sensitive example values only.

## Running the Application

### 1. Install Python dependencies

```powershell
uv sync --locked
```

### 2. Build and start Docker services

```powershell
docker compose up -d --build
```

### 3. Check container status

```powershell
docker compose ps
```

The expected services are:

- `api`
- `postgres`
- `redis`
- `worker`
- `nginx`

### 4. Initialize the database

If the database tables have not been created:

```powershell
docker compose exec api python -m devops_api.init_db
```

### 5. Verify the API

Open:

```text
http://127.0.0.1:8081/health
```

Expected response:

```json
{
  "status": "healthy"
}
```

Interactive API documentation:

```text
http://127.0.0.1:8081/docs
```

## API Endpoints

| Method | Endpoint           | Description               |
| ------ | ------------------ | ------------------------- |
| GET    | `/health`          | Application health check  |
| POST   | `/tasks`           | Create and enqueue a task |
| GET    | `/tasks`           | List tasks                |
| GET    | `/tasks/{task_id}` | Retrieve a task           |

### Create a Task

Request:

```http
POST /tasks
Content-Type: application/json
```

Body:

```json
{
  "title": "Verify background processing"
}
```

A successful request returns HTTP `201 Created` with task details.

Example response:

```json
{
  "id": 1,
  "title": "Verify background processing",
  "status": "pending",
  "created_at": "2026-11-21T00:00:00Z"
}
```

The ID and timestamp are illustrative. The task status may change asynchronously.

### Retrieve a Task

```http
GET /tasks/1
```

Example response after successful background processing:

```json
{
  "id": 1,
  "title": "Verify background processing",
  "status": "completed",
  "created_at": "2026-11-21T00:00:00Z"
}
```

### Task Status Values

| Status       | Meaning                              |
| ------------ | ------------------------------------ |
| `pending`    | Task created and awaiting processing |
| `processing` | Background processing underway       |
| `completed`  | Processing finished successfully     |
| `failed`     | Background processing failed         |

### Error Responses

| Status code | Meaning                              |
| ----------- | ------------------------------------ |
| 404         | Task not found                       |
| 422         | Invalid request data                 |
| 503         | Background task dispatch unavailable |

If task dispatch fails after the database commit, the task record may remain saved even though the API returns HTTP 503.

## Gunicorn Configuration

The application runs through Gunicorn with Uvicorn workers.

| Setting          | Value          |
| ---------------- | -------------- |
| Workers          | 2              |
| Bind address     | `0.0.0.0:8000` |
| Timeout          | 60 seconds     |
| Graceful timeout | 30 seconds     |
| Keep-alive       | 5 seconds      |
| Maximum requests | 1,000          |
| Request jitter   | 100            |
| Log level        | `info`         |

These values are initial development settings. Production deployments should tune them based on workload and available resources.

## Automated Testing

The project includes seven API tests.

| Test                   | Purpose                                  |
| ---------------------- | ---------------------------------------- |
| Health endpoint        | Verify HTTP 200 and response body        |
| Create task            | Verify task creation and Celery dispatch |
| Empty task title       | Verify request validation                |
| List tasks             | Verify task listing                      |
| Retrieve existing task | Verify task retrieval                    |
| Retrieve missing task  | Verify HTTP 404                          |
| Celery unavailable     | Verify HTTP 503                          |

Tests use dependency overrides and mocks to isolate database operations and Celery dispatch.

Run all tests:

```powershell
uv run pytest tests -v
```

Last verified local result:

```text
7 passed
```

A non-blocking Starlette deprecation warning was observed during testing.

## Code Quality

### Ruff Linting

```powershell
uv run ruff check src tests
```

### Ruff Formatting

```powershell
uv run ruff format --check src tests
```

### Static Type Checking

```powershell
uv run mypy src
```

### Automated Tests

```powershell
uv run pytest tests -v
```

All four checks passed locally during Day 27 development.

## Continuous Integration

GitHub Actions workflow:

```text
.github/workflows/day27-ci.yml
```

The workflow is designed to run:

1. Repository checkout
2. uv installation
3. Python 3.12 setup
4. Dependency installation
5. Ruff linting
6. Ruff formatting verification
7. mypy static type checking
8. pytest automated tests

The workflow is configured for pushes, pull requests, and manual execution.

**CI status:** Workflow created locally; successful execution on GitHub Actions has not yet been verified.

## Useful Docker Commands

Check services:

```powershell
docker compose ps
```

View API logs:

```powershell
docker compose logs api --tail=50
```

View Celery logs:

```powershell
docker compose logs worker --tail=50
```

Restart services:

```powershell
docker compose restart
```

Stop services:

```powershell
docker compose down
```

The `docker compose down` command preserves named volumes by default. Avoid `docker compose down -v` unless you intentionally want to remove persisted database and Redis data.

## Security Considerations

The project follows several basic security practices:

- Application container runs as a non-root user.
- `.env` is excluded from Git.
- Docker build excludes unnecessary local files.
- PostgreSQL and Redis are not directly published to the host.
- Nginx is bound to the local loopback interface.
- API requests use Pydantic validation.
- Tests isolate external dependencies.

This is a local development and learning project, not a hardened internet-facing deployment.

Additional production measures would include HTTPS, authentication, authorization, secret management, dependency scanning, monitoring, and appropriate network controls.

## Learning Outcomes

Through Day 27, this project demonstrates:

- Building multi-stage Docker images
- Managing multiple services with Docker Compose
- Integrating PostgreSQL, Redis, and Celery
- Serving FastAPI with Gunicorn and Uvicorn
- Configuring Nginx as a reverse proxy
- Running asynchronous background jobs
- Managing application environment variables
- Writing isolated API tests
- Enforcing code quality with Ruff and mypy
- Creating a GitHub Actions CI workflow

## Author

**YashKhadse01**

Part of the **30 Days of Backend Development** learning journey.

## Project Status

- [x] FastAPI endpoints implemented
- [x] PostgreSQL integration verified
- [x] Redis and Celery integration verified
- [x] Multi-stage Dockerfile implemented
- [x] Docker Compose services running
- [x] Gunicorn/Uvicorn configured
- [x] Nginx reverse proxy verified
- [x] Ruff linting and formatting passed
- [x] mypy type checking passed
- [x] Seven automated tests passed
- [x] GitHub Actions workflow created
- [x] GitHub Actions pipeline verified green

**Day 27 deliverable:** A containerized backend with automated quality checks and a GitHub Actions CI pipeline pending remote verification.
