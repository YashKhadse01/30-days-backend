# Day 5 — Raw HTTP JSON Server

## Project Overview

A lightweight HTTP JSON API server built using Python's built-in `socket` module, without Flask, Django, FastAPI, or any third-party web framework.

The project demonstrates how backend servers accept TCP connections, parse HTTP requests, route API endpoints, validate JSON data, and construct HTTP responses.

## Purpose of the Project

The main purpose is to understand how HTTP servers work internally before using backend frameworks.

It provides practical experience with networking, request-response communication, HTTP methods, status codes, routing, and error handling.

## Real-World Applications

The concepts demonstrated in this project are useful for:

- Understanding the networking layer behind web frameworks.
- Developing and debugging REST-style APIs.
- Learning how browsers and HTTP clients communicate with servers.
- Building small educational network services.
- Preparing for Python backend development interviews.

This project is educational and is not intended for production deployment.

## Project Structure

```text
raw_http_server/
├── app.py
├── server.py
├── test_app.py
├── test_server.py
├── test_api_manual.py
└── README.md
```

## File Responsibilities

| File | Responsibility |
|---|---|
| `app.py` | API routing, user management, and input validation |
| `server.py` | TCP connections, HTTP parsing, and response generation |
| `test_app.py` | Automated business-logic tests |
| `test_server.py` | Automated HTTP parsing and response tests |
| `test_api_manual.py` | Manual end-to-end API testing |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/health` | Server health check |
| GET | `/users` | Retrieve all users |
| GET | `/users/{id}` | Retrieve a specific user |
| POST | `/users` | Create a new user |

## Running the Server

Requirements: Python 3.11 or later.

```powershell
python server.py
```

The server starts at:

`http://127.0.0.1:8003`

## Testing the API

Check server health:

```powershell
curl.exe -i http://127.0.0.1:8003/health
```

Retrieve users:

```powershell
curl.exe -i http://127.0.0.1:8003/users
```

Create a user using a UTF-8 JSON file:

```powershell
curl.exe -i -X POST http://127.0.0.1:8003/users -H "Content-Type: application/json" --data-binary "@request.json"
```

## Automated Testing

Install testing dependencies:

```powershell
uv pip install pytest pytest-cov
```

Run tests:

```powershell
python -m pytest -v --cov=app --cov=server --cov-report=term-missing
```

### Verified Results

- 36 automated tests passed.
- `app.py`: 100% statement coverage.
- `server.py`: 66% statement coverage.
- Combined statement coverage: 77%.

## Current Limitations

- Handles one client connection at a time.
- Stores user data in memory, not a database.
- Does not support HTTPS.
- Does not implement the complete HTTP specification.
- Does not provide authentication or authorization.
- Not suitable for deployment on a public network.

## Future Improvements

- Add concurrency for multiple clients.
- Implement persistent database storage.
- Improve HTTP request validation and error handling.
- Add authentication and authorization.
- Implement additional REST endpoints.
- Introduce a production-ready framework such as FastAPI or Django.

## Skills Demonstrated

Python, TCP sockets, HTTP/1.1 basics, REST-style API routing, JSON handling, input validation, error handling, pytest, and code coverage.
