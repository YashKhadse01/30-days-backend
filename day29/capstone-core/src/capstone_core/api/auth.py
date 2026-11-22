from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from capstone_core.auth.security import (
    create_access_token,
    create_two_factor_challenge,
    decode_access_token,
)
from capstone_core.core.config import get_settings
from capstone_core.db.session import get_db
from capstone_core.models.two_factor import TwoFactorAuth
from capstone_core.models.user import User
from capstone_core.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    TwoFactorChallengeResponse,
    UserResponse,
)
from capstone_core.services.users import (
    DuplicateEmailError,
    authenticate_user,
    create_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        return await create_user(session, data.email, data.password)
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc


@router.post(
    "/login",
    response_model=TokenResponse | TwoFactorChallengeResponse,
)
async def login(
    data: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse | TwoFactorChallengeResponse:
    user = await authenticate_user(session, data.email, data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    two_factor = await session.get(TwoFactorAuth, user.id)

    if two_factor is not None and two_factor.is_enabled:
        challenge = create_two_factor_challenge(
            subject=str(user.id),
            secret_key=get_settings().jwt_secret_key,
        )
        return TwoFactorChallengeResponse(challenge_token=challenge)

    token = create_access_token(
        subject=str(user.id),
        secret_key=get_settings().jwt_secret_key,
    )

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        subject = decode_access_token(
            credentials.credentials,
            get_settings().jwt_secret_key,
        )
        user_id = UUID(subject)
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = await session.get(User, user_id)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
