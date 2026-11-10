
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
)
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from redis.asyncio import Redis

from auth_hardening.audit_log import AuditEvent, AuditLogger
from auth_hardening.lockout import BruteForceProtector
from auth_hardening.password_reset import PasswordResetManager
from auth_hardening.rate_limiter import SlidingWindowRateLimiter


# --------------------------------------------------
# Application lifespan and Redis initialization
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(
        os.getenv(
            "REDIS_URL",
            "redis://127.0.0.1:6379/0",
        ),
        decode_responses=True,
    )

    app.state.redis = redis
    app.state.limiter = SlidingWindowRateLimiter(redis)
    app.state.protector = BruteForceProtector(redis)
    app.state.audit = AuditLogger(redis)
    app.state.password_reset = PasswordResetManager(redis)

    try:
        await redis.ping()
        yield
    finally:
        await redis.aclose()


app = FastAPI(
    title="Day 16 - Authentication Hardening",
    description=(
        "Redis-backed authentication security demonstrations "
        "including rate limiting, account lockout, "
        "password reset tokens, and audit logging."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------
# Home endpoint
# --------------------------------------------------

@app.get("/")
async def home():
    return {
        "message": "Day 16 Authentication Hardening API",
        "status": "running",
    }


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
async def health(request: Request):
    await request.app.state.redis.ping()

    return {
        "status": "healthy",
        "service": "auth-hardening",
    }


# --------------------------------------------------
# Redis sliding-window rate limiter
# --------------------------------------------------

@app.get("/demo/rate-limit")
async def rate_limit_demo(request: Request):
    """Allow five requests per client within 60 seconds."""

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    # Test-only identity override.
    # Never enable DAY16_TESTING in production.
    if os.getenv("DAY16_TESTING") == "1":
        test_identity = request.headers.get(
            "X-Test-Client-ID"
        )

        if test_identity:
            client_ip = f"test:{test_identity}"

    allowed = await request.app.state.limiter.allow(
        f"demo:{client_ip}",
        limit=5,
        window_seconds=60,
    )

    if not allowed:
        await request.app.state.audit.log(
            AuditEvent.RATE_LIMITED,
            ip_address=client_ip,
        )

        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests",
            },
            headers={
                "Retry-After": "60",
            },
        )

    return {
        "message": "Request allowed",
    }


# --------------------------------------------------
# Brute-force account lockout
# --------------------------------------------------

class FailedLoginRequest(BaseModel):
    account: str


@app.post("/demo/login-failure")
async def simulate_failed_login(
    payload: FailedLoginRequest,
    request: Request,
):
    """Demonstrate account lockout after failed logins."""

    account = payload.account.strip().casefold()

    if not account:
        raise HTTPException(
            status_code=422,
            detail="Account identifier required",
        )

    protector = request.app.state.protector
    audit = request.app.state.audit

    if await protector.is_locked(account):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many login attempts",
            },
            headers={
                "Retry-After": "300",
            },
        )

    locked = await protector.record_failure(account)

    await audit.log(
        AuditEvent.LOGIN_FAILURE,
    )

    if locked:
        await audit.log(
            AuditEvent.ACCOUNT_LOCKED,
        )

        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many login attempts",
            },
            headers={
                "Retry-After": "300",
            },
        )

    return JSONResponse(
        status_code=401,
        content={
            "detail": "Invalid credentials",
        },
    )


# --------------------------------------------------
# Password reset request models
# --------------------------------------------------

class ResetTokenRequest(BaseModel):
    user_id: str = Field(min_length=1)


class ResetTokenConsumeRequest(BaseModel):
    token: str = Field(min_length=1)


# --------------------------------------------------
# Demo API key authorization
# --------------------------------------------------

def require_demo_key(
    x_demo_key: str | None = Header(default=None),
):
    """Protect local demonstration endpoints."""

    expected_key = os.getenv(
        "DAY16_DEMO_KEY",
        "",
    )

    if not expected_key:
        raise HTTPException(
            status_code=503,
            detail="Demo endpoint not configured",
        )

    if not secrets.compare_digest(
        x_demo_key or "",
        expected_key,
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )


# --------------------------------------------------
# Create password reset token
# --------------------------------------------------

@app.post(
    "/demo/password-reset/create",
    dependencies=[
        Depends(require_demo_key),
    ],
)
async def create_demo_reset_token(
    payload: ResetTokenRequest,
    request: Request,
):
    """Generate a single-use password reset token."""

    manager = request.app.state.password_reset

    token = await manager.create_token(
        payload.user_id
    )

    await request.app.state.audit.log(
        AuditEvent.PASSWORD_RESET_REQUESTED,
        user_id=payload.user_id,
    )

    # Local demonstration only.
    # Never expose reset tokens through public APIs.
    return {
        "reset_token": token,
    }


# --------------------------------------------------
# Consume password reset token
# --------------------------------------------------

@app.post(
    "/demo/password-reset/consume",
    dependencies=[
        Depends(require_demo_key),
    ],
)
async def consume_demo_reset_token(
    payload: ResetTokenConsumeRequest,
    request: Request,
):
    """Consume a reset token exactly once."""

    manager = request.app.state.password_reset

    user_id = await manager.consume_token(
        payload.token
    )

    if user_id is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token",
        )

    # Token validation only.
    # This endpoint does not change passwords.
    return {
        "message": "Reset token consumed",
        "user_id": user_id,
    }
