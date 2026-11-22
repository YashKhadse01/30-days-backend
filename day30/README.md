# Day 30 — Deployment, Performance Testing & Security Audit

**30 Days of Backend Development | Final Day**

## Project Overview

Day 30 marks the final stage of the **30-Day Backend Development Roadmap**, focusing on deploying, securing, testing, and validating the advanced FastAPI capstone developed on Day 29.

The application was containerized using Docker and deployed to Render, with Neon PostgreSQL serving as the cloud database and Upstash Redis supporting caching, rate limiting, and idempotency.

The final phase also includes live API integration testing, controlled performance testing, dependency vulnerability scanning, HTTP security hardening, and technical documentation.

### Live API Demo

[**🚀 Open Swagger UI — Interactive API Documentation**](https://capstone-core-api.onrender.com/docs)

Swagger UI provides interactive documentation for exploring the application's endpoints, request schemas, response formats, and authentication requirements.

**Additional Resources**

| Resource                       | Link                                                                     |
| ------------------------------ | ------------------------------------------------------------------------ |
| **Live API Demo (Swagger UI)** | [Open Swagger UI](https://capstone-core-api.onrender.com/docs)           |
| Health Check                   | [View API Health](https://capstone-core-api.onrender.com/health)         |
| OpenAPI Specification          | [View OpenAPI JSON](https://capstone-core-api.onrender.com/openapi.json) |
| GitHub Repository              | [View Source Code](https://github.com/YashKhadse01/30-days-backend)      |

> **Note:** The root URL (`/`) is not implemented and returns HTTP 404. Use `/docs` to access the interactive API documentation. Render Free instances may experience additional startup latency after inactivity.

---

## 1. Project Objectives

The primary objectives of Day 30 were to:

- Containerize and deploy the Day 29 FastAPI capstone.
- Configure cloud-hosted PostgreSQL using Neon.
- Integrate Upstash Redis for caching, rate limiting, and idempotency.
- Apply database schema migrations using Alembic.
- Verify API endpoints over HTTPS.
- Test user registration, login, JWT authentication, and protected endpoints.
- Validate Redis-backed API-key authentication and idempotent operations.
- Conduct controlled performance testing.
- Perform a dependency vulnerability audit.
- Implement and verify HTTP security headers.
- Document deployment architecture, test results, security findings, and limitations.

## 2. Project Structure

```text
30-days-backend/
│
├── day29/
│   └── capstone-core/
│       ├── alembic/
│       ├── docs/
│       ├── scripts/
│       ├── src/
│       ├── tests/
│       ├── Dockerfile
│       ├── compose.yaml
│       ├── compose.prod.yaml
│       ├── pyproject.toml
│       ├── uv.lock
│       └── README.md
│
├── day30/
│   ├── README.md
│   └── docs/
│       ├── deployment.md
│       ├── security-audit.md
│       ├── performance-testing.md
│       └── final-verification.md
│
└── README.md
```

**Day 29** contains the application source code, configuration, and automated tests.

**Day 30** contains deployment, performance, security audit, and verification documentation.

## 3. Technology Stack

| Category                       | Technology              |
| ------------------------------ | ----------------------- |
| Programming Language           | Python 3.12             |
| Backend Framework              | FastAPI                 |
| ASGI Server                    | Uvicorn                 |
| Data Validation                | Pydantic                |
| Database                       | PostgreSQL 16           |
| Cloud Database                 | Neon                    |
| ORM                            | SQLAlchemy Async        |
| Database Migrations            | Alembic                 |
| Caching                        | Redis                   |
| Cloud Redis                    | Upstash                 |
| Background Task Implementation | Celery                  |
| Authentication                 | JWT, API Keys, TOTP 2FA |
| Containerization               | Docker                  |
| Cloud Hosting                  | Render                  |
| Package Management             | uv                      |
| Automated Testing              | pytest                  |
| Dependency Security Audit      | pip-audit               |
| Version Control                | Git & GitHub            |
| API Documentation              | OpenAPI / Swagger UI    |

## 4. Cloud Deployment Architecture

The FastAPI backend is deployed as a Docker-based web service on Render.

Neon PostgreSQL stores application data, while Upstash Redis supports cache and API infrastructure features.

```text
                     CLIENT
                        |
                        | HTTPS
                        v
                +------------------+
                |   Render Cloud   |
                |   Web Service    |
                +------------------+
                        |
                        v
                +------------------+
                | Docker Container |
                | FastAPI/Uvicorn  |
                +------------------+
                        |
             +----------+----------+
             |                     |
             v                     v
    +------------------+  +------------------+
    | Neon PostgreSQL  |  | Upstash Redis    |
    |                  |  |                  |
    | User Data        |  | Caching          |
    | Authentication   |  | Rate Limiting    |
    | Alembic Schema   |  | Idempotency      |
    +------------------+  +------------------+
```

### Cloud Infrastructure

| Component             | Configuration       |
| --------------------- | ------------------- |
| Hosting Provider      | Render              |
| Deployment Type       | Docker Web Service  |
| Service Name          | `capstone-core-api` |
| Database Provider     | Neon                |
| Database Engine       | PostgreSQL 16       |
| Redis Provider        | Upstash             |
| Infrastructure Region | Singapore           |
| HTTPS                 | Enabled             |
| Application Port      | `10000`             |

## 5. Deployment Implementation

### Docker Containerization

The application uses a Dockerfile to package its Python runtime, dependencies, and FastAPI source code.

Docker provides a consistent runtime environment for deploying the backend to Render.

### PostgreSQL Integration

A Neon PostgreSQL database was configured for persistent application data.

The application connects using SQLAlchemy Async with the `asyncpg` driver.

Database migrations were applied using Alembic.

```powershell
uv run alembic upgrade head
```

Verified migration revision:

`e7ff44976ed1`

Verified database tables:

- `users`
- `two_factor_auth`
- `oauth_identities`
- `alembic_version`

### Redis Integration

Upstash Redis was configured using a TLS-enabled connection.

Redis supports:

- API rate limiting
- JSON caching
- Idempotency state management
- Redis-backed API infrastructure

### Environment Configuration

The deployed application uses the following environment variables:

```dotenv
DATABASE_URL=<configured-in-render>
REDIS_URL=<configured-in-render>
JWT_SECRET_KEY=<configured-in-render>
TOTP_ENCRYPTION_KEY=<configured-in-render>
API_KEY_SHA256=<configured-in-render>
PORT=10000
```

Actual credentials are stored outside the Git repository.

## 6. Live API Verification

The deployed API was tested over HTTPS.

### Authentication Verification

The following workflow was successfully tested:

```text
User Registration
       |
       v
POST /auth/register
       |
       v
User Stored in Neon PostgreSQL
       |
       v
POST /auth/login
       |
       v
JWT Access Token Generated
       |
       v
GET /auth/me
       |
       v
Authenticated User Retrieved
```

### Verified Results

| Test                        | Result |
| --------------------------- | ------ |
| Health endpoint             | Passed |
| User registration           | Passed |
| PostgreSQL persistence      | Passed |
| User login                  | Passed |
| JWT generation              | Passed |
| Protected profile retrieval | Passed |
| API-key authentication      | Passed |
| Redis idempotency           | Passed |

### Redis API Integration

| Scenario                 | HTTP Status | Result |
| ------------------------ | ----------- | ------ |
| Missing API key          | 401         | Passed |
| Valid API key            | 200         | Passed |
| New idempotent operation | 201         | Passed |
| Repeated operation       | 200         | Passed |
| Conflicting payload      | 409         | Passed |

**Redis integration verification: 5/5 passed.**

## 7. Automated Testing

The application uses pytest for unit, integration, and security regression testing.

### Test Results

| Metric                | Result                |
| --------------------- | --------------------- |
| Total Tests           | 107                   |
| Passed                | 107                   |
| Failed                | 0                     |
| Warnings              | 8                     |
| Latest Execution Time | 6.90 seconds          |
| Previous Coverage     | 87.22%                |
| Updated Coverage      | Pending remeasurement |

### Run Automated Tests

Navigate to the capstone directory:

```powershell
cd day29/capstone-core
```

Run the complete test suite:

```powershell
uv run pytest -q
```

Run tests with coverage:

```powershell
uv run pytest -q --cov=capstone_core --cov-fail-under=80
```

> The 87.22% coverage measurement was recorded before the latest security-header regression test. Updated coverage has not yet been independently verified.

## 8. Performance Testing

A controlled performance smoke test was conducted against the live HTTPS health endpoint.

### Test Configuration

| Parameter      | Value                     |
| -------------- | ------------------------- |
| Endpoint       | `/health`                 |
| HTTP Method    | GET                       |
| Total Requests | 20                        |
| Concurrency    | 2                         |
| Environment    | Warm Render Instance      |
| Test Client    | Python ThreadPoolExecutor |

### Performance Results

| Metric               | Result               |
| -------------------- | -------------------- |
| Successful Requests  | 20/20                |
| Failed Requests      | 0                    |
| Average Latency      | 286.03 ms            |
| P95 Latency          | 533.52 ms            |
| Total Execution Time | 2.92 seconds         |
| Throughput           | 6.84 requests/second |

### Interpretation

All 20 requests completed successfully.

The test demonstrated basic endpoint responsiveness under limited concurrency.

These measurements do not represent maximum application capacity or production-grade load testing.

## 9. Security Audit

The Day 30 security audit included authentication review, secret protection, dependency vulnerability scanning, and HTTP response hardening.

### Authentication Security

The application implements:

- Argon2 password hashing.
- JWT access-token authentication.
- Token expiration validation.
- TOTP-based two-factor authentication.
- API-key authentication using SHA-256 digests.
- Constant-time API-key comparison.
- Redis-backed rate limiting.

### HTTP Security Headers

Three security headers were implemented in the FastAPI middleware.

| Header                   | Value         | Live Verification |
| ------------------------ | ------------- | ----------------- |
| `X-Content-Type-Options` | `nosniff`     | Passed            |
| `X-Frame-Options`        | `DENY`        | Passed            |
| `Referrer-Policy`        | `no-referrer` | Passed            |

**Live security-header verification: 3/3 passed.**

### Dependency Vulnerability Audit

The locked production dependencies were exported using `uv` and scanned with `pip-audit`.

**Audit Result: No known vulnerabilities found.**

The result applies to known advisories at the time of the scan and does not guarantee that the application is free from all vulnerabilities.

### Secret Management

- Private environment files excluded from Git.
- Production credentials configured through Render environment variables.
- API keys are not included in documentation.
- JWT and TOTP secrets are kept outside the repository.

## 10. GitHub and Render Deployment Verification

The security-hardening changes were committed and pushed to the GitHub repository.

### Deployment Details

| Property                  | Value             |
| ------------------------- | ----------------- |
| Git Branch                | `main`            |
| Docker Deployment Commit  | `1b43693`         |
| Security Hardening Commit | `c705d0a`         |
| Render Deployment         | Live              |
| Deployment Date           | November 22, 2026 |
| Live Health Check         | Passed            |
| Security Headers          | 3/3 Passed        |
| Automated Tests           | 107 Passed        |

### Latest Verified Commit

```text
c705d0a security(day30): harden HTTP headers and add regression test
```

The latest deployed security-hardening commit was verified using the live HTTPS API.

## 11. Known Limitations

This project is an educational backend capstone and is not intended to be represented as a fully production-certified enterprise platform.

Current limitations include:

- Render Free may spin down during inactivity.
- Google OAuth requires valid external credentials and live configuration.
- A dedicated cloud Celery worker has not been deployed.
- Redis idempotency does not guarantee exactly-once external side effects.
- Live HTTP 429 rate-limit behavior has not been independently verified.
- Performance testing was limited to the health endpoint.
- Comprehensive penetration testing was not performed.
- Production monitoring and alerting have not been fully established.

## 12. Technical Documentation

Detailed Day 30 reports are maintained in the `docs/` directory.

| Document                                                  | Description                                                                       |
| --------------------------------------------------------- | --------------------------------------------------------------------------------- |
| [Deployment Report](docs/deployment.md)                   | Docker, Render, Neon PostgreSQL, Upstash Redis, HTTPS, and migrations             |
| [Security Audit Report](docs/security-audit.md)           | Authentication, HTTP security headers, dependency audit, and security limitations |
| [Performance Testing Report](docs/performance-testing.md) | Test methodology, latency, throughput, and interpretation                         |
| [Final Verification Report](docs/final-verification.md)   | Automated tests, cloud integration, deployment status, and verification checklist |

## 13. Key Learning Outcomes

Through Day 30, the following practical backend engineering skills were demonstrated:

1. Containerizing a Python FastAPI application using Docker.
2. Deploying a backend application to a cloud hosting platform.
3. Connecting cloud-hosted PostgreSQL and Redis services.
4. Managing application secrets using environment variables.
5. Applying database migrations in a deployed environment.
6. Verifying authentication and protected API workflows.
7. Implementing and testing HTTP security headers.
8. Scanning Python dependencies for known vulnerabilities.
9. Conducting controlled API performance measurements.
10. Documenting technical results and operational limitations.

## 14. Conclusion

Day 30 successfully completed the deployment and scoped verification phase of the **30-Day Backend Development Roadmap**.

The FastAPI capstone was deployed to Render using Docker, integrated with Neon PostgreSQL and Upstash Redis, and verified through live API testing.

Security improvements were implemented and verified over HTTPS. The complete automated test suite passed, and the locked production dependency audit reported no known vulnerabilities.

### Final Verified Results

| Deliverable            | Result                         |
| ---------------------- | ------------------------------ |
| Cloud Deployment       | Successful                     |
| HTTPS Health Check     | Passed                         |
| PostgreSQL Integration | Passed                         |
| Redis Integration      | 5/5 Passed                     |
| Automated Tests        | 107 Passed                     |
| Performance Smoke Test | 20/20 Passed                   |
| HTTP Security Headers  | 3/3 Passed                     |
| Dependency Audit       | No Known Vulnerabilities Found |
| GitHub Deployment      | Verified                       |

The project demonstrates practical experience in backend development, cloud deployment, API security, automated testing, infrastructure integration, and technical documentation.

---

**Project:** 30 Days of Backend Development
**Day:** 30 — Final Deployment & Verification
**GitHub Repository:** [https://github.com/YashKhadse01/30-days-backend](https://github.com/YashKhadse01/30-days-backend)
**Live API Demo:** [https://capstone-core-api.onrender.com/docs](https://capstone-core-api.onrender.com/docs)
**Status:** Deployment and scoped verification completed