
import pytest

from auth_2fa_rbac.security import (
    hash_password,
    verify_password,
    needs_password_rehash,
)


def test_password_hash_created():
    hashed = hash_password("StrongPassword123!")

    assert hashed.startswith("$argon2id$")


def test_correct_password_accepted():
    password = "StrongPassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_wrong_password_rejected():
    hashed = hash_password("CorrectPassword123!")

    assert verify_password("WrongPassword", hashed) is False


def test_same_password_produces_different_hashes():
    password = "SamePassword123!"

    first = hash_password(password)
    second = hash_password(password)

    assert first != second


def test_plaintext_password_not_stored():
    password = "SensitivePassword123!"
    hashed = hash_password(password)

    assert password not in hashed


def test_invalid_hash_rejected():
    assert verify_password(
        "StrongPassword123!",
        "invalid-hash",
    ) is False


def test_empty_password_rejected():
    with pytest.raises(ValueError):
        hash_password("")


def test_password_hash_does_not_need_upgrade():
    hashed = hash_password("StrongPassword123!")

    assert needs_password_rehash(hashed) is False


def test_case_sensitive_password():
    hashed = hash_password("Password123!")

    assert verify_password("password123!", hashed) is False


def test_unicode_password_supported():
    password = "SecurePassword🔐123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True
