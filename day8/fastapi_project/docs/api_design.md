
# TaskFlow API — Backend System Design

## 1. Project Overview

TaskFlow is a RESTful Task Management API built using FastAPI.

It allows registered users to create, view, update, delete,
search, and manage their personal tasks securely.

The API will use PostgreSQL for persistent storage,
Pydantic for validation, and Docker for deployment.

## 2. Why Are We Building This Project?

The purpose is to practice designing and developing
a complete backend application.

It demonstrates:

- REST API design
- User authentication and authorization
- CRUD operations
- Database integration
- Input validation
- Error handling
- Automated testing
- Docker containerization

## 3. Role in Backend Development

A backend application receives client requests,
validates input, executes business logic,
communicates with a database, and returns responses.

TaskFlow demonstrates these responsibilities through
a practical task-management application.

Example:

Client requests GET /api/v1/tasks
    ↓
FastAPI matches the endpoint
    ↓
Authentication identifies the user
    ↓
Service layer applies business rules
    ↓
Database returns the user's tasks
    ↓
FastAPI sends a JSON response

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| FastAPI | HTTP API framework |
| Pydantic | Data validation |
| PostgreSQL | Persistent database |
| SQLAlchemy | Database ORM |
| Alembic | Database migrations |
| pytest | Automated testing |
| Docker | Containerization |
| Docker Compose | Multi-container orchestration |
| OpenAPI | API contract and documentation |

## 5. System Architecture

Client / Swagger UI
        |
        v
FastAPI Router
        |
        v
Authentication and Validation
        |
        v
Service Layer
        |
        v
Repository / ORM
        |
        v
PostgreSQL Database

The layers are separated so that routing,
business rules, and persistence can be tested
and maintained independently.

## 6. Database Entities

### User

- id: UUID, primary key
- email: unique string
- password_hash: string
- created_at: timestamp

Passwords must never be stored in plain text.

### Task

- id: UUID, primary key
- user_id: UUID, foreign key to User
- title: string, required
- description: optional string
- completed: boolean, default false
- priority: integer, 1 to 5
- created_at: timestamp
- updated_at: timestamp

Relationship:

One User → Many Tasks

Every task belongs to exactly one user.

## 7. API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | /api/v1/auth/register | Register a user |
| POST | /api/v1/auth/login | Log in |
| GET | /api/v1/tasks | List user's tasks |
| POST | /api/v1/tasks | Create a task |
| GET | /api/v1/tasks/{task_id} | Retrieve a task |
| PATCH | /api/v1/tasks/{task_id} | Update a task |
| DELETE | /api/v1/tasks/{task_id} | Delete a task |
| GET | /health | Application health |

## 8. Request Validation

Task creation requires:

- title: 3–100 characters
- description: optional, maximum 1000 characters
- priority: integer between 1 and 5

The server generates the task ID, user ID association,
completion default, and timestamps.

Clients must not be able to set another user's ID
when creating a task.

## 9. Authentication and Authorization

Authentication will use securely signed JWT access
tokens with expiration.

Passwords will be hashed using an appropriate
password-hashing algorithm.

Protected endpoints require a valid bearer token.

Users may access only their own tasks.

Unauthorized requests return HTTP 401.

Requests for tasks not owned by the user return
HTTP 404 to avoid exposing their existence.

## 10. API Response Codes

| Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Resource deleted |
| 400 | Invalid business request |
| 401 | Authentication required |
| 404 | Resource not found |
| 409 | Resource conflict |
| 422 | Request validation failed |
| 500 | Unexpected server error |

## 11. Search and Pagination

GET /api/v1/tasks supports:

- completed: optional boolean
- priority: optional integer, 1–5
- search: optional text query
- limit: default 20, maximum 100
- offset: default 0

Task listings will be restricted to the
authenticated user's records.

## 12. Testing Strategy

Automated tests will cover:

- Health endpoint
- User registration
- Duplicate email rejection
- Login success and failure
- Unauthorized requests
- Task creation
- Task retrieval
- Task updates
- Task deletion
- Input validation
- Search and pagination
- Cross-user access prevention

Database integration tests will use isolated
test data and repeatable setup/cleanup.

## 13. Docker Deployment

The final project will contain:

- Dockerfile for FastAPI
- compose.yaml for application and PostgreSQL
- Environment-based configuration
- Database initialization/migrations
- Health checks
- Startup instructions

Secrets and real credentials must not be committed.

## 14. Definition of Done — Day 18

The project is complete when:

- FastAPI endpoints are implemented
- PostgreSQL persistence works
- Authentication and authorization work
- Automated tests pass
- OpenAPI documentation is available
- Application runs successfully in Docker
- README contains setup and usage instructions

Public HTTPS deployment is reserved for the
final main project later in the roadmap.

## 15. Future Improvements

- Refresh tokens
- Role-based permissions
- Task deadlines and reminders
- Audit logging
- CI/CD pipeline
- Monitoring and metrics
- Public HTTPS hosting
