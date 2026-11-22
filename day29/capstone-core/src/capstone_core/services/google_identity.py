"""Resolve verified Google OpenID Connect identities to local users."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from capstone_core.models.oauth_identity import OAuthIdentity
from capstone_core.models.user import User


class GoogleIdentityError(Exception):
    """Base exception for Google identity resolution."""


class GoogleEmailConflictError(GoogleIdentityError):
    """Email belongs to an account not linked to this Google identity."""


class GoogleIdentityInactiveError(GoogleIdentityError):
    """The linked local user account is inactive."""


class GoogleIdentityInvalidError(GoogleIdentityError):
    """Google identity claims are missing or invalid."""


async def resolve_google_user(
    session: AsyncSession,
    *,
    subject: str,
    email: str,
    email_verified: bool,
) -> User:
    """Resolve an existing Google identity or create a new local user.

    Caller must validate the Google ID token before invoking this service.
    """
    if not isinstance(subject, str) or not subject.strip():
        raise GoogleIdentityInvalidError("Missing Google subject")

    if (
        not isinstance(email, str)
        or not email.strip()
        or not isinstance(email_verified, bool)
        or not email_verified
    ):
        raise GoogleIdentityInvalidError("Verified Google email required")

    normalized_email = email.strip().lower()

    result = await session.execute(
        select(OAuthIdentity).where(
            OAuthIdentity.provider == "google",
            OAuthIdentity.provider_subject == subject,
        )
    )

    identity = result.scalar_one_or_none()

    if identity is not None:
        user = await session.get(User, identity.user_id)

        if user is None or not user.is_active:
            raise GoogleIdentityInactiveError(
                "Google-linked account is unavailable"
            )

        return user

    result = await session.execute(
        select(User).where(User.email == normalized_email)
    )

    if result.scalar_one_or_none() is not None:
        raise GoogleEmailConflictError(
            "Email already belongs to another account"
        )

    user = User(
        email=normalized_email,
        password_hash=None,
        is_active=True,
    )

    session.add(user)

    try:
        await session.flush()

        session.add(
            OAuthIdentity(
                user_id=user.id,
                provider="google",
                provider_subject=subject,
            )
        )

        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise GoogleEmailConflictError(
            "Google identity or email already registered"
        ) from exc

    await session.refresh(user)
    return user
