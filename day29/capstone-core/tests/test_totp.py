import pyotp
import pytest

from capstone_core.auth.totp import (
    decrypt_totp_secret,
    encrypt_totp_secret,
    generate_provisioning_uri,
    generate_totp_secret,
    verify_totp_code,
)

TEST_KEY = "development-test-encryption-key-at-least-32-bytes"


def test_secret_generation() -> None:
    secret = generate_totp_secret()
    assert len(secret) >= 32
    assert pyotp.TOTP(secret).now()


def test_encryption_round_trip() -> None:
    secret = generate_totp_secret()
    encrypted = encrypt_totp_secret(secret, TEST_KEY)

    assert encrypted != secret
    assert decrypt_totp_secret(encrypted, TEST_KEY) == secret


def test_wrong_key_rejected() -> None:
    encrypted = encrypt_totp_secret(generate_totp_secret(), TEST_KEY)

    with pytest.raises(ValueError):
        decrypt_totp_secret(
            encrypted,
            "another-test-encryption-key-at-least-32-bytes",
        )


def test_short_encryption_key_rejected() -> None:
    with pytest.raises(ValueError):
        encrypt_totp_secret(generate_totp_secret(), "short")


def test_provisioning_uri() -> None:
    uri = generate_provisioning_uri(
        generate_totp_secret(),
        "test@example.com",
    )

    assert uri.startswith("otpauth://totp/")
    assert "Capstone%20Core" in uri


def test_valid_totp_code() -> None:
    secret = generate_totp_secret()
    code = pyotp.TOTP(secret).now()

    assert verify_totp_code(secret, code) is not None


def test_invalid_totp_code() -> None:
    secret = generate_totp_secret()

    assert verify_totp_code(secret, "abcdef") is None
    assert verify_totp_code(secret, "123") is None


def test_replayed_code_rejected() -> None:
    secret = generate_totp_secret()
    code = pyotp.TOTP(secret).now()

    accepted_step = verify_totp_code(secret, code)

    assert accepted_step is not None
    assert verify_totp_code(
        secret,
        code,
        last_used_step=accepted_step,
    ) is None
