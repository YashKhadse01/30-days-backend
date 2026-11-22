# Security Design

## Authentication

The application implements JWT authentication and password hashing using Argon2 through `pwdlib`.

Access tokens must be protected by a sufficiently long, unpredictable `JWT_SECRET_KEY`.

## Two-Factor Authentication

TOTP-based two-factor authentication is implemented using `pyotp`.

The configured `TOTP_ENCRYPTION_KEY` protects TOTP-related sensitive data. Treat this key as a secret and do not commit it.

## Google OAuth

Google OAuth support is implemented with Authlib.

Live OAuth requires valid Google client credentials and a correctly configured callback URL.

The application conditionally enables session middleware when `OAUTH_SESSION_SECRET` is configured. The session secret must contain at least 32 characters.

## Public API Keys

Public API endpoints require `X-API-Key`.

The server stores a SHA-256 digest of the API key in `API_KEY_SHA256` and uses constant-time digest comparison.

API keys must be generated securely and distributed outside the repository.

## Rate Limiting

Redis provides an atomic fixed-window rate limiter. Redis failures result in HTTP 503 rather than silently disabling the limit.

## Idempotency

Redis `SET NX EX` prevents simultaneous acquisition of the same key while its state exists.

Completion uses a Lua script to verify the fingerprint and ownership token atomically.

Current limitations:

- Keys are not yet namespaced by authenticated client.
- Redis lease expiration can allow a later request to reacquire a key.
- The implementation does not guarantee exactly-once external side effects.
- Durable transactional outbox and reconciliation are not implemented.

## Webhooks

Outgoing webhook delivery uses HMAC-SHA256 signing and HTTPS URL validation.

Before production use, add destination allowlisting or equivalent SSRF protection, delivery persistence, retry policies, and replay protection.

## Secrets and Deployment

- Never commit `.env`, API keys, tokens, or OAuth client secrets.
- Use HTTPS outside local development.
- Restrict database and Redis network access.
- Use unique production secrets.
- Rotate credentials when exposed.
- Perform dependency and security reviews before deployment.

## Current Validation Scope

Automated tests cover security logic, but production OAuth configuration, external webhook destinations, and live deployment security have not been fully validated.
