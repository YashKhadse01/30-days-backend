# Day 7 — Python Mini Web Framework

## Project Overview

A lightweight Python web framework built using Python's standard library, demonstrating how web frameworks handle HTTP requests, route matching, JSON responses, and REST APIs.

**Project:** To-Do REST API  
**Language:** Python 3.11  
**Testing:** pytest and pytest-cov  
**External web framework:** None

## Features

- Custom request and response classes
- Route registration using decorators
- Dynamic URL parameters
- HTTP method handling
- JSON request parsing and response serialization
- To-Do CRUD operations
- Error handling and input validation
- Automated API testing

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check server health |
| GET | `/todos` | List all To-Dos |
| POST | `/todos` | Create a To-Do |
| GET | `/todos/{id}` | Retrieve a To-Do |
| PUT | `/todos/{id}` | Update a To-Do |
| DELETE | `/todos/{id}` | Delete a To-Do |

## Running the Server

From the `mini_framework` directory:

```powershell
python server.py
```

The server runs at `http://127.0.0.1:8007`.

## Example Requests

Check health:

```powershell
curl.exe http://127.0.0.1:8007/health
```

List To-Dos:

```powershell
curl.exe http://127.0.0.1:8007/todos
```

Create a To-Do:

```powershell
$body = @{ title = "Learn Python" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8007/todos" -Method Post -ContentType "application/json" -Body $body
```

## Running Automated Tests

```powershell
uv run --with pytest --with pytest-cov python -m pytest test_app.py -v --cov=app --cov=main --cov-report=term-missing
```

## Test Results

- 23 automated tests passed
- 100% statement coverage across `app.py` and `main.py`
- CRUD and validation scenarios tested

## Learning Outcomes

This project demonstrates the fundamentals behind frameworks such as Flask, Django, and FastAPI, including request routing, HTTP response generation, API validation, and automated testing.

## Future Improvements

- PostgreSQL database integration
- Persistent To-Do storage
- Authentication and authorization
- Request middleware
- API documentation
- Deployment and containerization