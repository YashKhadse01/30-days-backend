from typing import Annotated
from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from capstone_core.api.auth import get_current_user
from capstone_core.auth.security import (
    create_access_token,
    decode_two_factor_challenge,
)
from capstone_core.core.config import get_settings
from capstone_core.db.session import get_db
from capstone_core.models.two_factor import TwoFactorAuth
from capstone_core.models.user import User
from capstone_core.schemas.auth import TokenResponse
from capstone_core.services.two_factor import (
    TwoFactorAlreadyEnabledError,
    begin_enrollment,
    confirm_enrollment,
    verify_login_totp,
)

router = APIRouter(prefix="/auth/2fa", tags=["Two-Factor Authentication"])


class SetupResponse(BaseModel):
    provisioning_uri: str


class ConfirmRequest(BaseModel):
    code: str = Field(pattern=r"^[0-9]{6}$")


class ConfirmResponse(BaseModel):
    enabled: bool


@router.post("/setup", response_model=SetupResponse)
async def setup_two_factor(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> SetupResponse:
    try:
        uri = await begin_enrollment(session, user.id, user.email)
    except TwoFactorAlreadyEnabledError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Two-factor authentication is already enabled",
        ) from exc

    return SetupResponse(provisioning_uri=uri)


@router.post("/confirm", response_model=ConfirmResponse)
async def confirm_two_factor(
    data: ConfirmRequest,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ConfirmResponse:
    verified = await confirm_enrollment(session, user.id, data.code)

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used verification code",
        )

    return ConfirmResponse(enabled=True)


class VerifyLoginRequest(BaseModel):
    challenge_token: str = Field(min_length=1)
    code: str = Field(pattern=r"^[0-9]{6}$")


@router.post("/verify-login", response_model=TokenResponse)
async def verify_two_factor_login(
    data: VerifyLoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired two-factor authentication challenge",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        subject = decode_two_factor_challenge(
            data.challenge_token,
            get_settings().jwt_secret_key,
        )
        user_id = UUID(subject)
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise unauthorized from exc

    user = await session.get(User, user_id)

    if user is None or not user.is_active:
        raise unauthorized

    configuration = await session.get(TwoFactorAuth, user_id)

    if configuration is None or not configuration.is_enabled:
        raise unauthorized

    if not await verify_login_totp(session, user_id, data.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or already used authentication code",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(user.id),
        secret_key=get_settings().jwt_secret_key,
    )

    return TokenResponse(access_token=access_token)
