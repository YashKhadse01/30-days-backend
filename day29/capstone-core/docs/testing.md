# Testing and Quality Assurance

## Test Framework

The project uses pytest, pytest-asyncio, pytest-cov, and Ruff.

## Run Tests

```powershell
uv run pytest -q
```

## Coverage

```powershell
uv run pytest -q --cov=capstone_core --cov-fail-under=80
```

Latest verified results:

- 106 tests passed
- 87.22% total coverage
- Required threshold: 80%
- 8 nonblocking warnings

Coverage varies as code and tests change.

## Linting

```powershell
uv run ruff check src tests
```

## Tested Components

- Authentication and JWT validation
- TOTP verification
- Google OAuth implementation with mocked integrations
- Redis caching
- Atomic Redis rate limiting
- Public API authentication
- Signed outgoing webhooks
- Third-party HTTP service
- Redis idempotency acquisition and completion
- Idempotent POST operation integration
- Celery task logic
- WebSocket behavior

## Integration Testing

`tests/test_operations.py` exercises the operations endpoint with a running Redis instance.

Start the configured Redis container before running this test.

The integration test covers:

1. Initial request returns HTTP 201.
2. Repeated request replays the original result with HTTP 200.
3. Reusing the same key with a different payload returns HTTP 409.
4. Missing API key returns HTTP 401.

## Known Warnings

The last test run reported:

- Authlib/httpx deprecation warning
- Starlette/httpx deprecation warning
- Short JWT secrets used in security tests

These warnings did not fail the suite. Production JWT secrets must be at least 32 bytes of unpredictable material for HS256.

## Before Deployment

Run the complete suite, review dependencies, test real OAuth configuration, validate background worker execution, and perform deployment-specific security checks.
