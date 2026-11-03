# Day 9 — Async Database Layer + Cursor-Based Pagination

## 30-Day Python Backend Development Roadmap

**Project:** Async Task API  
**Technology:** FastAPI, PostgreSQL, SQLAlchemy, asyncpg  
**Duration:** 5 hours  
**Status:** Implemented and tested — 9 integration tests passed

---

## 1. Project Overview

The Async Task API is a RESTful backend application built using FastAPI and PostgreSQL.

It supports creating, retrieving, updating, and deleting tasks through asynchronous database operations.

The project also implements cursor-based pagination to retrieve large collections of tasks efficiently.

Unlike an in-memory API, task records are stored persistently in PostgreSQL.

## 2. Why This Project Matters

Modern backend systems must handle concurrent HTTP requests while communicating with databases.

This project demonstrates:

- Asynchronous Python programming using `async` and `await`
- Database persistence with PostgreSQL
- Object-relational mapping using SQLAlchemy
- Database session management and transactions
- REST API design and HTTP status codes
- Pydantic request and response validation
- Cursor-based pagination
- Automated integration testing

These concepts are fundamental to production backend applications.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Programming language |
| FastAPI | REST API framework |
| PostgreSQL 18 | Relational database |
| SQLAlchemy 2.x | Asynchronous ORM |
| asyncpg | Async PostgreSQL driver |
| Pydantic | Data validation |
| Uvicorn | ASGI server |
| pytest | Automated testing |
| pytest-asyncio | Async test support |
| HTTPX | HTTP integration testing |
| uv | Dependency management |

## 4. Project Architecture

```text
HTTP Client / Swagger UI
          |
          v
FastAPI Endpoints (main.py)
          |
          v
Pydantic Validation (schemas.py)
          |
          v
CRUD Operations (crud.py)
          |
          v
SQLAlchemy AsyncSession (database.py)
          |
          v
asyncpg Driver
          |
          v
PostgreSQL Database (day9_tasks)
```

## 5. Project Structure

```text
async_task_api/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── main.py
├── tests/
│   └── test_tasks.py
├── check_db.py
├── create_tables.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## 6. Database Design

Database: `day9_tasks`

Table: `tasks`

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key |
| title | VARCHAR(100) | Task title |
| description | TEXT | Optional description |
| completed | BOOLEAN | Completion status |
| created_at | TIMESTAMPTZ | Creation timestamp |

The `id` column has a primary-key B-tree index, which supports efficient keyset pagination.

## 7. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Application health check |
| POST | `/tasks` | Create task |
| GET | `/tasks` | List tasks with pagination |
| GET | `/tasks/{task_id}` | Retrieve task |
| PATCH | `/tasks/{task_id}` | Update task |
| DELETE | `/tasks/{task_id}` | Delete task |

### Create Task

Request:

```json
{
  "title": "Learn Async SQLAlchemy",
  "description": "Practice PostgreSQL CRUD operations"
}
```

Successful response: `201 Created`.

### Update Task

```json
{
  "title": "Master Async PostgreSQL",
  "completed": true
}
```

Successful response: `200 OK`.

### Delete Task

Successful response: `204 No Content`.

## 8. Cursor-Based Pagination

The API supports keyset pagination using the task ID as a cursor.

Example:

```http
GET /tasks?limit=2&cursor=2
```

Response structure:

```json
{
  "items": [
    {"id": 3, "title": "Task 3", "description": null, "completed": false, "created_at": "2026-11-03T00:00:00Z"},
    {"id": 4, "title": "Task 4", "description": null, "completed": false, "created_at": "2026-11-03T00:00:00Z"}
  ],
  "next_cursor": 4,
  "has_more": true
}
```

The query uses:

```sql
SELECT *
FROM tasks
WHERE id > 2
ORDER BY id ASC
LIMIT 3;
```

For a page size of two, one additional row is fetched to determine whether another page exists.

**Benefits:**

- Avoids large offset scans
- Supports efficient incremental data retrieval
- Suitable for Load More and infinite scrolling interfaces
- Uses an indexed ordering key

This educational implementation uses integer cursors. Production systems may require opaque cursors, compound ordering keys, and consistency handling.

## 9. Installation and Setup

### Prerequisites

- Python 3.11+
- PostgreSQL
- uv

### Install Dependencies

```powershell
uv sync
```

### Create PostgreSQL Databases

Using `psql`:

```sql
CREATE DATABASE day9_tasks;
CREATE DATABASE day9_tasks_test;
```

### Configure Environment Variables

Create `.env` from `.env.example` and configure:

```dotenv
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/day9_tasks
TEST_DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/day9_tasks_test
```

Never commit `.env` or real credentials.

### Create Tables

```powershell
uv run python create_tables.py
```

### Start the Application

```powershell
uv run uvicorn app.main:app --reload --port 8000
```

### Open Swagger UI

http://127.0.0.1:8000/docs

## 10. Automated Integration Testing

Tests run against the separate PostgreSQL database `day9_tasks_test`.

Execute:

```powershell
uv run python -m pytest tests/test_tasks.py -v
```

Verified results:

| Test | Result |
|---|---|
| Health endpoint | Passed |
| Create task | Passed |
| Retrieve task | Passed |
| Update task | Passed |
| Delete task | Passed |
| Missing task | Passed |
| Invalid title | Passed |
| Cursor pagination | Passed |
| Invalid pagination limit | Passed |

**Total: 9 passed, 0 failed.**

The test fixture overrides the database dependency and resets tables in the designated test database.

**Warning:** The integration tests recreate tables in `day9_tasks_test`. Never point the test configuration at a database containing important data.

## 11. Challenges and Solutions

### Missing greenlet Dependency

**Problem:** SQLAlchemy async functionality could not initialize.

**Solution:**

```powershell
uv add "sqlalchemy[asyncio]"
```

### Async pytest Fixture Error

**Problem:** pytest did not recognize the asynchronous test client fixture.

**Solution:** Used `@pytest_asyncio.fixture` for the asynchronous fixture.

### Database Isolation

**Challenge:** Tests must not modify development data.

**Solution:** Created a separate PostgreSQL test database and added database-name verification before resetting tables.

## 12. Real-World Applications

The same architecture can support:

- E-commerce product APIs
- Inventory management systems
- Project management applications
- Customer relationship management systems
- Order processing backends
- Paginated activity feeds

## 13. Future Improvements

- Alembic database migrations
- JWT authentication and authorization
- Advanced filtering and sorting
- Opaque cursor encoding
- Database performance benchmarking
- Docker and Docker Compose
- CI/CD integration
- Improved concurrency and transaction tests

## 14. Day 9 Learning Outcomes

By completing this project, we learned how to:

1. Connect FastAPI asynchronously to PostgreSQL.
2. Define SQLAlchemy ORM models.
3. Implement database-backed CRUD operations.
4. Manage asynchronous database sessions.
5. Validate requests and responses with Pydantic.
6. Implement cursor-based pagination.
7. Test FastAPI using HTTPX and pytest.
8. Isolate integration tests from development data.
9. Debug missing dependencies and async fixture errors.

**Day 9 deliverable achieved: A working asynchronous PostgreSQL CRUD API with cursor-based pagination and automated integration tests.**