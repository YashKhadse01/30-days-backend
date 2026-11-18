# Day 24 — Reliable Webhook Delivery System

A Django REST Framework application demonstrating asynchronous outgoing webhooks using Celery and Redis.

## Features

- Admin-protected webhook endpoint registration API
- HMAC-SHA256 signed webhook payloads with timestamps
- Celery-based asynchronous HTTP delivery
- Automatic retries with exponential backoff
- Database-backed delivery and attempt logs
- Sequential duplicate-delivery protection
- Celery Beat periodic monitoring
- Local receiver that verifies signatures and rejects duplicate events

## Technology Stack

Python 3.12, Django, Django REST Framework, Celery, Redis, django-celery-beat, SQLite, Requests, uv, and Ruff.

## Project Structure

- `config/` — Django configuration and Celery integration
- `webhooks/models.py` — Endpoint, event, delivery, and attempt models
- `webhooks/tasks.py` — Celery delivery and monitoring tasks
- `webhooks/delivery.py` — Signed HTTP transport
- `webhooks/signing.py` — HMAC signing and verification
- `webhooks/serializers.py` — Endpoint validation
- `webhooks/views.py` — Registration API
- `receiver.py` — Local signature-verifying receiver
- `failure_receiver.py` — Simulated HTTP 500 receiver
- `webhooks/test_*.py` — Automated tests

## Local Setup

Install dependencies:

```powershell
uv sync
```

Apply migrations:

```powershell
uv run python manage.py migrate
```

Start a local Redis container:

```powershell
docker run -d --name day24-redis -p 127.0.0.1:6379:6379 redis:7-alpine
```

If the container already exists, start it using `docker start day24-redis`.

Start the Celery worker:

```powershell
uv run celery -A config worker --loglevel=info --pool=solo
```

Start Celery Beat in another terminal:

```powershell
uv run celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Start the local receiver in another terminal:

```powershell
$env:WEBHOOK_RECEIVER_SECRET="replace-with-a-long-random-local-secret"
uv run python receiver.py
```

Use the same secret when registering the corresponding local webhook endpoint.

## Registration API

Staff-authenticated endpoints:

- `GET /api/webhooks/endpoints/`
- `POST /api/webhooks/endpoints/`
- `GET /api/webhooks/endpoints/{id}/`
- `PATCH /api/webhooks/endpoints/{id}/`
- `DELETE /api/webhooks/endpoints/{id}/`

Signing secrets are write-only in API responses.

## Retry Policy

The delivery worker makes up to four attempts with exponential retry delays of 1, 2, and 4 seconds.

Retryable failures include network exceptions, HTTP 408, 425, 429, and 5xx responses. Individual attempts are recorded in the database.

## Testing

Run the complete Django test suite:

```powershell
uv run python manage.py test webhooks -v 1
```

Run code-quality checks:

```powershell
uv run ruff check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

Verified local result: 15 tests passed.

## Security and Engineering Limitations

This is an educational implementation, not a production-ready webhook service.

- SQLite does not provide the row-locking guarantees required for robust concurrent delivery claiming.
- Receiver deduplication is held in memory and does not survive restarts.
- Endpoint URL validation does not fully prevent SSRF.
- Webhook signing secrets are not encrypted at rest.
- Interrupted worker tasks need durable recovery handling.
- Webhook delivery is at-least-once, not exactly-once.

## Roadmap

Day 24 of the 30-day backend development roadmap: Celery, Redis, retries, idempotent tasks, Celery Beat, and outgoing HMAC-signed webhooks.