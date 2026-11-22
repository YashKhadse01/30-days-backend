"""Regression tests for Google-only passwordless accounts."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from capstone_core.models.user import User
from capstone_core.services.users import authenticate_user


@pytest.mark.asyncio
async def test_google_only_user_cannot_login_with_password() -> None:
    user = User(
        id=uuid4(),
        email="google-only@example.com",
        password_hash=None,
        is_active=True,
    )

    session = AsyncMock()

    with (
        patch(
            "capstone_core.services.users.get_user_by_email",
            new_callable=AsyncMock,
            return_value=user,
        ),
        patch(
            "capstone_core.services.users.verify_password",
        ) as verify_password,
    ):
        result = await authenticate_user(
            session,
            "google-only@example.com",
            "AnyPassword123!",
        )

    assert result is None
    verify_password.assert_not_called()
