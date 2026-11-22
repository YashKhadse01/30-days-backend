import asyncio
import time
import uuid

import pyotp
import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from capstone_core.auth.totp import encrypt_totp_secret
from capstone_core.core.config import get_settings
from capstone_core.models.two_factor import TwoFactorAuth
from capstone_core.models.user import User
from capstone_core.services.two_factor import verify_login_totp


@pytest.mark.asyncio
async def test_concurrent_totp_code_can_only_be_used_once():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    user_id = uuid.uuid4()
    email = f"concurrency-{user_id.hex}@example.com"
    secret = pyotp.random_base32()

    # Use the next TOTP step, which falls within the accepted window.
    current_step = int(time.time()) // 30
    accepted_step = current_step + 1
    code = pyotp.TOTP(secret).at(accepted_step * 30)

    try:
        async with session_factory() as session:
            session.add(
                User(
                    id=user_id,
                    email=email,
                    password_hash="integration-test-only",
                    is_active=True,
                )
            )
            await session.flush()
            session.add(
                TwoFactorAuth(
                    user_id=user_id,
                    encrypted_secret=encrypt_totp_secret(
                        secret,
                        settings.totp_encryption_key,
                    ),
                    is_enabled=True,
                    last_used_step=current_step,
                )
            )
            await session.commit()

        async def attempt_verification() -> bool:
            async with session_factory() as session:
                return await verify_login_totp(
                    session,
                    user_id,
                    code,
                )

        results = await asyncio.gather(
            attempt_verification(),
            attempt_verification(),
        )

        assert sorted(results) == [False, True], results

        async with session_factory() as session:
            config = await session.get(TwoFactorAuth, user_id)
            assert config is not None
            assert config.last_used_step == accepted_step

    finally:
        async with session_factory() as session:
            await session.execute(
                delete(User).where(User.id == user_id)
            )
            await session.commit()

        await engine.dispose()
