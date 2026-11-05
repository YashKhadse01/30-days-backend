
import logging

import pytest

from secure_auth_api.email_service import send_verification_email
from secure_auth_api.database import settings


def test_development_email_sender(monkeypatch, caplog):
    monkeypatch.setattr(settings, "app_env", "development")

    with caplog.at_level(logging.WARNING):
        send_verification_email(
            "test@example.com",
            "dummy-test-token",
        )

    assert "test@example.com" in caplog.text
    assert "dummy-test-token" in caplog.text


def test_email_sender_blocked_in_production(monkeypatch):
    monkeypatch.setattr(settings, "app_env", "production")

    with pytest.raises(RuntimeError):
        send_verification_email(
            "test@example.com",
            "dummy-test-token",
        )
