# API Reference

## Interactive Documentation

FastAPI generates an OpenAPI schema at `/openapi.json`.

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Registered HTTP Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/register` | Register a user |
| POST | `/auth/login` | Authenticate a user |
| GET | `/auth/me` | Retrieve authenticated user details |
| GET | `/auth/google/login` | Begin Google OAuth |
| GET | `/auth/google/callback` | Handle Google OAuth callback |
| POST | `/auth/2fa/setup` | Start TOTP setup |
| POST | `/auth/2fa/confirm` | Confirm TOTP setup |
| POST | `/auth/2fa/verify-login` | Verify a TOTP login |
| GET | `/api/v1/catalog` | Retrieve demonstration catalog |
| POST | `/api/v1/operations` | Create or replay a demonstration operation |
| GET | `/health` | Health response |

For exact request and response schemas, consult `/docs`.

## Public API Authentication

The versioned public API requires an `X-API-Key` header. The application compares the SHA-256 digest of the supplied key with the configured `API_KEY_SHA256`.

An invalid or missing key returns HTTP 401. Missing or invalid server configuration returns HTTP 503.

## Rate Limiting

The public API enforces 60 requests per 60-second window for each API-key identity using Redis.

Exceeding the limit returns HTTP 429 with a `Retry-After` header.

## Idempotent Operations

`POST /api/v1/operations` requires:

- `X-API-Key`: valid configured API key
- `Idempotency-Key`: nonempty key of at most 128 characters
- JSON object request body

Example body:

```json
{
  "amount": 100
}
```

Responses:

| Status | Meaning |
|---|---|
| 201 | New demonstration operation created |
| 200 | Previously completed result replayed |
| 409 | Conflicting payload, processing request, or unavailable completed result |
| 401 | Missing or invalid API key |
| 429 | Rate limit exceeded |
| 503 | Required Redis service unavailable |

Idempotency is currently a Redis-backed demonstration. It does not guarantee exactly-once external side effects.

## WebSocket

The source defines a WebSocket echo handler at `/ws/echo`. WebSocket endpoints do not appear in the standard OpenAPI HTTP path listing.

## Additional Services

Webhook delivery and third-party HTTP integration are implemented as service modules. They are not exposed as public HTTP endpoints in the verified route list.
