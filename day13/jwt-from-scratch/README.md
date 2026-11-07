
# Day 13 — JWT Authentication From Scratch

## Project Overview

A Python implementation of JSON Web Tokens (JWTs) without using a JWT library.

Built as part of a 30-day Python Backend Development roadmap.

The project demonstrates:

- HS256 JWT signing and verification using HMAC-SHA256
- RS256 JWT signing and verification using RSA and SHA-256
- Base64URL encoding and decoding
- JWT claims validation
- Refresh-token rotation
- Refresh-token reuse detection
- Access-token revocation
- Automated security testing

## Why This Project Matters

JWTs are widely used in backend authentication and authorization.

Implementing their core mechanisms helps explain:

- How JWT signatures prevent tampering
- The difference between symmetric and asymmetric cryptography
- How backend services validate token claims
- Why token expiration and revocation are important
- How refresh-token rotation reduces the risk of stolen tokens

This is an educational implementation, not a replacement for a maintained production JWT library.

## Technologies

| Technology | Purpose |
|---|---|
| Python 3.11 | Core programming language |
| uv | Dependency and project management |
| cryptography | RSA key generation and RS256 operations |
| hashlib | SHA-256 hashing |
| hmac | HS256 signing and constant-time verification |
| secrets | Secure random token generation |
| pytest | Automated testing |
| pytest-cov | Test coverage reporting |

## Project Architecture

```text
JWT Payload
    |
    v
Base64URL Encoding
    |
    v
HS256 / RS256 Signing
    |
    v
JWT (header.payload.signature)
    |
    v
Signature Verification
    |
    v
Claims Validation
    |
    v
Revocation Check
    |
    v
Authenticated Claims
```

Refresh-token handling is a separate workflow that includes rotation and reuse detection.

## Project Structure

```text
jwt-from-scratch/
|
|-- src/
|   |-- jwt_from_scratch/
|       |-- __init__.py
|       |-- encoding.py
|       |-- hs256.py
|       |-- rs256.py
|       |-- claims.py
|       |-- jwt_decoder.py
|       |-- refresh.py
|       |-- revocation.py
|
|-- tests/
|   |-- test_hs256.py
|   |-- test_rs256.py
|   |-- test_claims.py
|   |-- test_jwt_decoder.py
|   |-- test_revocation.py
|   |-- additional refresh-token tests
|
|-- pyproject.toml
|-- README.md
```

## JWT Structure

A JWT contains three Base64URL-encoded segments:

```text
header.payload.signature
```

The header identifies the algorithm, the payload contains claims, and the signature provides integrity protection.

JWT payloads are encoded, not encrypted. Sensitive information should not be placed in ordinary JWT payloads.

## HS256 and RS256

### HS256

HS256 uses a shared secret and HMAC-SHA256.

The same secret is used for signing and verification.

### RS256

RS256 uses asymmetric cryptography:

- Private key: signs the JWT
- Public key: verifies the signature

The implementation uses RSA with PKCS#1 v1.5 signature padding and SHA-256.

## JWT Claims

The validator checks:

- `exp`: expiration time
- `iat`: issued-at time
- `nbf`: not-before time
- `jti`: unique token identifier
- `aud`: intended audience

It also validates timestamp types and rejects unsupported or invalid claims.

## Refresh-Token Security

Refresh-token rotation issues a replacement token when a valid refresh token is used.

Reuse detection identifies attempts to reuse an already rotated token.

The project also implements token revocation to reject invalidated access tokens.

## Installation

From the project directory:

```powershell
uv sync --dev
```

## Running Tests

Run the complete test suite:

```powershell
uv run pytest -q
```

Generate a coverage report:

```powershell
uv run pytest tests/ --cov=jwt_from_scratch --cov-report=term-missing
```

Generate HTML coverage:

```powershell
uv run pytest tests/ --cov=jwt_from_scratch --cov-report=html
```

## Verified Test Results

At the time of documentation:

- Automated tests: **71 passed**
- Overall statement coverage: **95%**
- Test execution time: approximately **1–2 seconds**

Security tests include:

- Valid and invalid signatures
- Wrong signing secrets and public keys
- Algorithm mismatch
- Expired and future-dated tokens
- Invalid audiences
- Missing or malformed claims
- Refresh-token reuse
- Revoked JWT rejection

## Security Considerations

- Never commit private keys or production secrets.
- Use strong, securely generated HS256 secrets.
- Restrict accepted JWT algorithms explicitly.
- Validate signatures before trusting claims.
- Validate issuer and audience for production integrations.
- Use HTTPS when transporting tokens.
- Store refresh tokens securely.
- Avoid logging complete authentication tokens.
- Limit token lifetimes and rotate signing keys safely.

## Current Limitations

- Educational implementation rather than a production JWT framework.
- In-memory token state is not suitable for distributed deployments.
- Persistent revocation storage is not yet implemented.
- Issuer validation and key rotation need additional work.
- Further fuzzing and security testing are recommended.

## Future Improvements

- Redis-backed revocation and refresh-token storage
- Signing-key rotation and key identifiers
- Issuer validation
- FastAPI authentication integration
- Token size limits and stricter parsing
- Additional security and concurrency tests

## Learning Outcomes

This project demonstrates practical understanding of JWT internals, HMAC, RSA, cryptographic signatures, claim validation, token lifecycle management, and automated security testing.
