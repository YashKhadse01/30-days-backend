# Day 30 — Security Audit Report

## Objective

Review authentication, secret handling, dependency security,
HTTP response hardening, and live deployment behavior.

## Security Controls Reviewed

### Authentication

The capstone implements:

- Argon2 password hashing through pwdlib.
- JWT access tokens signed with HS256.
- JWT expiration and required-claim validation.
- Distinct access-token and 2FA-challenge token types.
- TOTP-based two-factor authentication.

### Public API Security

The versioned public API requires an `X-API-Key` header.

The server stores a SHA-256 digest of the API key and
uses constant-time comparison.

Redis provides rate limiting and idempotency state.

Configured rate limit: 60 requests per 60 seconds per API-key identity.

### Secret Management

Verified local files excluded from Git:

- `.env.day30.local`
- `.env.production`

Actual credentials must remain outside Git.

The `.env.example` template contains three values that were
flagged for manual placeholder review:

- `POSTGRES_PASSWORD`
- `JWT_SECRET_KEY`
- `TOTP_ENCRYPTION_KEY`

Their actual values were not displayed or independently verified
during the audit.

## HTTP Security Headers

The following middleware headers were implemented:

| Header | Expected value |
|---|---|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| Referrer-Policy | no-referrer |

A regression test was added in:

`day29/capstone-core/tests/test_security_headers.py`

All three headers were verified against the live HTTPS
health endpoint using Python httpx.

Live verification: 3 of 3 headers passed.

HSTS and Content Security Policy were not added during this
step; deployment behavior and Swagger UI compatibility
require separate consideration.

## Dependency Vulnerability Audit

Tool: `pip-audit`, executed through `uvx`.

Production dependencies were exported from the locked
dependency graph.

Audit result:

**No known vulnerabilities found.**

This reflects known advisories at scan time. It is not
proof that the application has no vulnerabilities.

## Automated Security Verification

The complete suite passed:

**107 tests passed, 8 warnings.**

Warnings included third-party HTTP-client deprecations
and short JWT signing keys used in some tests.

Production signing keys should use at least 32 bytes of
unpredictable material for HS256.

## Known Security Limitations

- Redis idempotency keys are not namespaced by client.
- Idempotency does not guarantee exactly-once external effects.
- Live OAuth was not configured or verified.
- Webhook delivery requires further SSRF and replay protections.
- No comprehensive penetration test was performed.
- No dedicated cloud worker security review was performed.

## Conclusion

The implemented security improvements passed automated
regression testing and live HTTPS header verification.

The system remains an educational backend capstone and
must not be represented as fully production-security-certified.
