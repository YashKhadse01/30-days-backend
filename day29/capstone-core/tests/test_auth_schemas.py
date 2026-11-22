import pytest
from pydantic import ValidationError

from capstone_core.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


def test_registration_normalizes_email() -> None:
    data = RegisterRequest(
        email="TEST@EXAMPLE.COM",
        password="StrongPassword123!",
    )
    assert data.email == "test@example.com"


def test_registration_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="test@example.com",
            password="short",
        )


def test_registration_rejects_invalid_email() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(
            email="invalid-email",
            password="StrongPassword123!",
        )


def test_login_normalizes_email() -> None:
    data = LoginRequest(
        email="TEST@EXAMPLE.COM",
        password="StrongPassword123!",
    )
    assert data.email == "test@example.com"


def test_token_response() -> None:
    token = TokenResponse(access_token="example-token")

    assert token.token_type == "bearer"
