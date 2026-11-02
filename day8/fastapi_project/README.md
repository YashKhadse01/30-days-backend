
# Day 8 — FastAPI Core + API Design

## 30-Day Python Backend Development Roadmap

### Objective

Learn professional API development using FastAPI,
Pydantic, automated testing, and design-first OpenAPI.

## Why This Project Matters

Backend applications need reliable routing, input
validation, business logic, API documentation,
and automated testing.

FastAPI provides these capabilities through Python
type hints, Pydantic, and OpenAPI integration.

Day 8 connects our custom web framework from Day 7
with modern production-oriented API development.

## Part 1 — FastAPI Practice Application

File: `practice_api.py`

Features:

- Health endpoint
- Dynamic path parameters
- Task creation and retrieval
- Pydantic request validation
- Query parameter filtering
- Automatic Swagger documentation
- HTTP error handling

Run:

```powershell
uv run uvicorn practice_api:app --reload --port 8000
```

Swagger UI: http://127.0.0.1:8000/docs

## Part 2 — TaskFlow API Skeleton

Entry point: `app/main.py`

This modular FastAPI application is the starting
architecture for our Day 18 project.

Current implementation:

- Application entry point
- Modular APIRouter
- Health endpoint
- Pydantic response schema
- Generated OpenAPI documentation

Run:

```powershell
uv run uvicorn app.main:app --reload --port 8001
```

Swagger UI: http://127.0.0.1:8001/docs

## Design-First Documentation

`docs/api_design.md`

Contains the proposed TaskFlow requirements,
architecture, database entities, security model,
endpoint design, testing strategy, and Docker plan.

`docs/openapi.yaml`

Contains the validated OpenAPI 3.0.3 contract
for the future Day 18 application.

The specification describes planned functionality.
Authentication, PostgreSQL integration, and task
CRUD are not yet implemented in the skeleton.

## Automated Testing

Run all tests:

```powershell
uv run python -m pytest -v
```

Verified results:

- Practice API: 7 passed
- TaskFlow skeleton: 3 passed
- Total: 10 passed

## Technology Stack

- Python 3.11
- FastAPI
- Pydantic
- Uvicorn
- pytest
- HTTPX
- OpenAPI 3.0.3
- uv

## Future Improvements

- PostgreSQL integration
- User registration and login
- JWT authentication
- Persistent task CRUD
- Database migrations
- Docker and Docker Compose
- Additional integration and security tests

## Day 8 Outcome

Designed and tested a FastAPI application,
created a modular backend skeleton, and produced
a validated design-first OpenAPI specification
for the Day 18 TaskFlow project.
