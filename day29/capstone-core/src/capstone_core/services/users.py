from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from capstone_core.auth.security import hash_password, verify_password
from capstone_core.models.user import User


class DuplicateEmailError(Exception):
    """Raised when a registration email already exists."""


async def get_user_by_email(
    session: AsyncSession,
    email: str,
) -> User | None:
    normalized_email = email.strip().lower()

    result = await session.execute(
        select(User).where(User.email == normalized_email)
    )

    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User:
    normalized_email = email.strip().lower()

    existing = await get_user_by_email(session, normalized_email)

    if existing is not None:
        raise DuplicateEmailError("Email already registered")

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
        is_active=True,
    )

    session.add(user)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise DuplicateEmailError("Email already registered") from exc

    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    user = await get_user_by_email(session, email)

    if user is None:
        return None

    if not user.is_active:
        return None

    if user.password_hash is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
