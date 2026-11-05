
import email

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy import update
from secure_auth_api.schemas import EmailVerificationRequest
from secure_auth_api.tokens import is_token_expired
from secure_auth_api.email_service import send_verification_email
import logging

logger = logging.getLogger(__name__)

from secure_auth_api.database import get_db
from secure_auth_api.models import User, EmailVerificationToken
from secure_auth_api.schemas import UserRegister, UserResponse
from secure_auth_api.security import hash_password
from secure_auth_api.validators import validate_password
from secure_auth_api.tokens import (
    generate_verification_token,
    hash_verification_token,
    get_token_expiry,
)


app = FastAPI(
    title="Day 11 - Secure Authentication API",
    version="0.1.0",
)


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    # Step 1: Validate password strength
    try:
        validate_password(data.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    # Step 2: Normalize email
    email = str(data.email).lower()

    # Step 3: Check for an existing user
    result = await db.execute(
        select(User).where(User.email == email)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Unable to register with these details",
        )

    # Step 4: Create user with hashed password
    user = User(
        email=email,
        password_hash=hash_password(data.password),
        is_verified=False,
    )

    db.add(user)

    try:
        # Step 5: Insert user and obtain user ID
        await db.flush()

        # Step 6: Generate a secure verification token
        raw_token = generate_verification_token()

        # Step 7: Store only the token hash
        verification = EmailVerificationToken(
            user_id=user.id,
            token_hash=hash_verification_token(raw_token),
            expires_at=get_token_expiry(),
        )

        db.add(verification)

        # Step 8: Save user and token atomically
        await db.commit()

    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Unable to register with these details",
        ) from exc

    # Step 9: Refresh user from database
    await db.refresh(user)

    # Step 10: Attempt verification email delivery
    try:
        send_verification_email(email, raw_token)
    except RuntimeError:
        logger.exception(
        "Verification email delivery unavailable for user ID %s",
        user.id,
    )

    # Step 11: Return safe user response
    return user


@app.post("/auth/verify-email")
async def verify_email(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    # Hash the submitted token before searching.
    token_hash = hash_verification_token(data.token)

    # Lock the token row to prevent concurrent reuse.
    result = await db.execute(
        select(EmailVerificationToken)
        .where(EmailVerificationToken.token_hash == token_hash)
        .with_for_update()
    )

    verification = result.scalar_one_or_none()

    # Use the same generic error for invalid or used tokens.
    if verification is None or verification.used_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token",
        )

    if is_token_expired(verification.expires_at):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token",
        )

    # Mark the user as verified.
    result = await db.execute(
        update(User)
        .where(User.id == verification.user_id)
        .values(is_verified=True)
        .returning(User.id)
    )

    if result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token",
        )

    # Mark the token as used.
    verification.used_at = datetime.now(timezone.utc)

    # Commit both changes atomically.
    await db.commit()

    return {"message": "Email verified successfully"}
