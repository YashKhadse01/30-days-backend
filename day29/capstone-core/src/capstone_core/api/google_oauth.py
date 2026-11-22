"""Google OpenID Connect login initiation."""

from typing import Annotated

from authlib.integrations.base_client import OAuthError
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from capstone_core.auth.security import (
    create_access_token,
    create_two_factor_challenge,
)
from capstone_core.core.config import get_settings
from capstone_core.db.session import get_db
from capstone_core.models.two_factor import TwoFactorAuth
from capstone_core.schemas.auth import (
    TokenResponse,
    TwoFactorChallengeResponse,
)
from capstone_core.services.google_identity import (
    GoogleEmailConflictError,
    GoogleIdentityInactiveError,
    GoogleIdentityInvalidError,
    resolve_google_user,
)

router = APIRouter(prefix="/auth/google", tags=["Authentication"])

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


def create_google_oauth_client(
    client_id: str,
    client_secret: str,
) -> OAuth:
    """Configure the Google OpenID Connect client."""
    oauth = OAuth()

    oauth.register(
        name="google",
        client_id=client_id,
        client_secret=client_secret,
        server_metadata_url=GOOGLE_DISCOVERY_URL,
        client_kwargs={"scope": "openid email profile"},
        code_challenge_method="S256",
    )

    return oauth


@router.get("/login", include_in_schema=True)
async def google_login(request: Request):
    """Redirect the browser to Google's authorization endpoint."""
    settings = get_settings()

    if not (
        settings.google_client_id
        and settings.google_client_secret
        and settings.oauth_session_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is not configured",
        )

    oauth = create_google_oauth_client(
        settings.google_client_id,
        settings.google_client_secret,
    )

    return await oauth.google.authorize_redirect(
        request,
        settings.google_redirect_uri,
        code_challenge_method="S256",
    )


@router.get(
    "/callback",
    response_model=TokenResponse | TwoFactorChallengeResponse,
)
async def google_callback(
    request: Request,
    response: Response,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse | TwoFactorChallengeResponse:
    """Exchange Google's authorization code and authenticate the user."""
    response.headers["Cache-Control"] = "no-store"

    settings = get_settings()

    if not (
        settings.google_client_id
        and settings.google_client_secret
        and settings.oauth_session_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google login is not configured",
        )

    oauth = create_google_oauth_client(
        settings.google_client_id,
        settings.google_client_secret,
    )

    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google authentication failed",
        ) from exc

    # Authlib validates the OIDC ID token, including its nonce,
    # before populating the verified userinfo claims.
    if not token.get("id_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google ID token is missing",
        )

    claims = token.get("userinfo")

    if not isinstance(claims, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Verified Google identity is missing",
        )

    try:
        user = await resolve_google_user(
            session,
            subject=claims.get("sub"),
            email=claims.get("email"),
            email_verified=claims.get("email_verified") is True,
        )
    except GoogleIdentityInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google identity is invalid",
        ) from exc
    except GoogleEmailConflictError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already belongs to another account",
        ) from exc
    except GoogleIdentityInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is unavailable",
        ) from exc

    two_factor = await session.get(TwoFactorAuth, user.id)

    if two_factor is not None and two_factor.is_enabled:
        challenge = create_two_factor_challenge(
            subject=str(user.id),
            secret_key=settings.jwt_secret_key,
        )
        return TwoFactorChallengeResponse(challenge_token=challenge)

    access_token = create_access_token(
        subject=str(user.id),
        secret_key=settings.jwt_secret_key,
    )

    return TokenResponse(access_token=access_token)
