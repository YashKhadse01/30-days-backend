"""Tests for optional Google OAuth configuration."""

from capstone_core.core.config import Settings


def test_oauth_session_secret_is_optional() -> None:
    field = Settings.model_fields["oauth_session_secret"]

    assert field.default is None


def test_google_callback_has_local_default() -> None:
    field = Settings.model_fields["google_redirect_uri"]

    assert (
        field.default
        == "http://127.0.0.1:8765/auth/google/callback"
    )
