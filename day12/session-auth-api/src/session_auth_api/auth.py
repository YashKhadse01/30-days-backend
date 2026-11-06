
from datetime import datetime, timezone
from fastapi import Request
from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from session_auth_api.database import get_db, settings
from session_auth_api.models import Session, User
from session_auth_api.sessions import hash_session_token


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_token: str | None = Cookie(
        default=None,
        alias=settings.session_cookie_name,
    ),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Not authenticated",
    )

    if not session_token:
        raise unauthorized

    token_hash = hash_session_token(session_token)

    result = await db.execute(
        select(Session).where(
            Session.token_hash == token_hash,
            Session.revoked_at.is_(None),
            Session.expires_at > datetime.now(timezone.utc),
        )
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise unauthorized

    user = await db.get(User, session.user_id)

    if user is None:
        raise unauthorized

    return user

async def get_current_session(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Session:
    raw_token = request.cookies.get(settings.session_cookie_name)

    if not raw_token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    result = await db.execute(
        select(Session).where(
            Session.token_hash == hash_session_token(raw_token),
            Session.revoked_at.is_(None),
            Session.expires_at > datetime.now(timezone.utc),
        )
    )

    session = result.scalar_one_or_none()

    if session is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
        )

    return session
