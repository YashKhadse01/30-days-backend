import uuid

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from capstone_core.auth.totp import (
    decrypt_totp_secret,
    encrypt_totp_secret,
    generate_provisioning_uri,
    generate_totp_secret,
    verify_totp_code,
)
from capstone_core.core.config import get_settings
from capstone_core.models.two_factor import TwoFactorAuth


class TwoFactorAlreadyEnabledError(Exception):
    """Raised when an enabled 2FA configuration would be replaced."""


async def begin_enrollment(
    session: AsyncSession,
    user_id: uuid.UUID,
    email: str,
) -> str:
    """Store an encrypted, inactive secret and return its provisioning URI."""
    existing = await session.get(TwoFactorAuth, user_id)

    if existing is not None and existing.is_enabled:
        raise TwoFactorAlreadyEnabledError("2FA is already enabled")

    secret = generate_totp_secret()
    encrypted = encrypt_totp_secret(
        secret,
        get_settings().totp_encryption_key,
    )

    if existing is None:
        session.add(
            TwoFactorAuth(
                user_id=user_id,
                encrypted_secret=encrypted,
                is_enabled=False,
                last_used_step=None,
            )
        )
    else:
        existing.encrypted_secret = encrypted
        existing.is_enabled = False
        existing.last_used_step = None

    await session.commit()

    return generate_provisioning_uri(secret, email)


async def confirm_enrollment(
    session: AsyncSession,
    user_id: uuid.UUID,
    code: str,
) -> bool:
    """Enable 2FA after successful code verification."""
    config = await session.get(TwoFactorAuth, user_id)

    if config is None or config.is_enabled:
        return False

    secret = decrypt_totp_secret(
        config.encrypted_secret,
        get_settings().totp_encryption_key,
    )

    accepted_step = verify_totp_code(
        secret,
        code,
        last_used_step=config.last_used_step,
    )

    if accepted_step is None:
        return False

    result = await session.execute(
        update(TwoFactorAuth)
        .where(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.is_enabled.is_(False),
            TwoFactorAuth.last_used_step.is_(None),
        )
        .values(
            is_enabled=True,
            last_used_step=accepted_step,
        )
    )

    if result.rowcount != 1:
        await session.rollback()
        return False

    await session.commit()
    return True


async def verify_login_totp(
    session: AsyncSession,
    user_id: uuid.UUID,
    code: str,
) -> bool:
    """Accept a valid code only once, including concurrent requests."""
    config = await session.get(TwoFactorAuth, user_id)

    if config is None or not config.is_enabled:
        return False

    secret = decrypt_totp_secret(
        config.encrypted_secret,
        get_settings().totp_encryption_key,
    )

    accepted_step = verify_totp_code(
        secret,
        code,
        last_used_step=config.last_used_step,
    )

    if accepted_step is None:
        return False

    result = await session.execute(
        update(TwoFactorAuth)
        .where(
            TwoFactorAuth.user_id == user_id,
            TwoFactorAuth.is_enabled.is_(True),
            (
                (TwoFactorAuth.last_used_step.is_(None))
                | (TwoFactorAuth.last_used_step < accepted_step)
            ),
        )
        .values(last_used_step=accepted_step)
    )

    if result.rowcount != 1:
        await session.rollback()
        return False

    await session.commit()
    return True
