# System Architecture

## Overview

Capstone Core is a modular FastAPI backend built to demonstrate advanced backend development patterns.

```text
HTTP / WebSocket Clients
          |
          v
     FastAPI Application
          |
          +-- Authentication / JWT / TOTP / Google OAuth
          |
          +-- Public API / API Key / Rate Limiting
          |
          +-- Idempotent Operations
          |
          +-- WebSocket Echo
          |
          v
       Services
          |
          +-- PostgreSQL / Async SQLAlchemy
          +-- Redis / Cache / Rate Limits / Idempotency
          +-- Celery / Background Tasks
          +-- External HTTP APIs
          +-- Signed Webhook Delivery
```

## Component Responsibilities

### API Layer

`src/capstone_core/api/` defines request handling, authentication endpoints, public API routes, OAuth flows, two-factor verification, and WebSocket behavior.

### Authentication

`src/capstone_core/auth/` handles JWT and TOTP-related security functionality.

### Database

`src/capstone_core/db/` contains database configuration. SQLAlchemy models represent application data, and Alembic manages schema migrations.

### Redis

Redis supports JSON caching, rate limiting, and idempotency state.

Rate limiting uses an atomic Redis Lua script. The configured public API limit is 60 requests per 60-second window per authenticated API-key identity.

### Idempotency

The operations endpoint acquires a Redis key, processes a demonstration operation, and stores its result for replay. A Lua script checks the operation fingerprint and ownership token before completion.

The current key namespace is not scoped per client. This must be addressed before a multi-tenant deployment.

### Celery

Celery provides background task functionality. Live worker execution should be verified separately before deployment.

### External Integrations

Dedicated services implement outbound HTTP requests and signed webhook delivery. These are service-level integrations rather than fully deployed business workflows.

## Configuration

Runtime configuration is loaded from environment variables using Pydantic Settings.

`.env.example` documents expected variables. Actual secrets belong in `.env` or a secure secret manager.

## Deployment Limitations

Production deployment requires additional work, including HTTPS, operational monitoring, secret management, reliable background worker infrastructure, and a deployment-specific security review.
