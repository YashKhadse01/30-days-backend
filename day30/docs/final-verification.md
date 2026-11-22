# Day 30 — Final Verification Report

## Objective

Record the verified state of the deployed backend and
identify remaining work and limitations.

## Verification Checklist

| Check | Result |
|---|---|
| Docker deployment on Render | Passed |
| Live HTTPS health endpoint | Passed |
| Neon PostgreSQL connection | Passed |
| Alembic migrations | Passed |
| Live registration | Passed |
| Live JWT login | Passed |
| Protected profile endpoint | Passed |
| Redis API-key authentication | Passed |
| Redis idempotent operations | Passed |
| Controlled health load test | Passed |
| Security header regression test | Passed |
| Live security headers | Passed |
| Locked dependency audit | No known vulnerabilities found |
| Full automated test suite | 107 passed |
| GitHub security-hardening push | Passed |

## Live Redis Integration

Five observed outcomes:

1. Missing API key returned HTTP 401.
2. Valid API key returned HTTP 200.
3. New idempotent operation returned HTTP 201.
4. Replayed operation returned HTTP 200 with the same ID.
5. Conflicting payload returned HTTP 409.

These checks do not establish that every Redis failure mode
or the configured HTTP 429 rate limit was tested live.

## Automated Tests

Latest verified test result:

**107 passed, 8 warnings.**

The previously measured coverage was 87.22% with 106 tests.

Coverage has not yet been remeasured after the additional
security-header regression test. Do not report 87.22%
as the latest coverage result.

## Deployment Verification

Public URL:

https://capstone-core-api.onrender.com

Latest verified security-hardening commit:

`c705d0a`

Render reported the commit live on November 22, 2026.

Independent HTTPS verification returned:

- HTTP 200
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- Referrer-Policy: no-referrer

## Outstanding Limitations

- Google OAuth needs live external configuration.
- A cloud Celery worker is not deployed.
- Webhook delivery is not verified as a complete
  cloud-hosted business workflow.
- Rate-limit HTTP 429 behavior was not verified live.
- Comprehensive production monitoring is not established.
- A full penetration test has not been conducted.
- Updated test coverage percentage is pending.

## Final Assessment

The Day 30 cloud deployment, basic performance smoke test,
dependency audit, and HTTP security hardening have been
successfully verified within their stated scope.

The capstone is a deployed educational demonstration,
not a fully production-certified enterprise system.
