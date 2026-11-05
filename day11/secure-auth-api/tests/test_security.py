import pytest
from secure_auth_api.security import hash_password, verify_password
from secure_auth_api.validators import validate_password

def test_hash_password():
    password = "StrongPass123!"
    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("scrypt$")

def test_correct_password():
    password = "StrongPass123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True

def test_wrong_password():
    hashed = hash_password("StrongPass123!")

    assert verify_password("WrongPass123!", hashed) is False

def test_unique_salts():
    password = "StrongPass123!"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    assert hash1 != hash2
    assert verify_password(password, hash1)
    assert verify_password(password, hash2)

@pytest.mark.parametrize(
    "password",
    [
        "short123!",
        "lowercase123!",
        "UPPERCASE123!",
        "NoNumbersHere!",
        "NoSpecial1234",
        "A" * 129,
    ],
)
def test_weak_passwords(password):
    with pytest.raises(ValueError):
        validate_password(password)

def test_valid_password():
    assert validate_password("StrongPass123!") == "StrongPass123!"

@pytest.mark.parametrize(
    "stored_hash",
    [
        "",
        "invalid",
        "bcrypt$123",
        "scrypt$invalid$8$1$abc$def",
        "scrypt$16384$8$1$abc$def",
    ],
)
def test_malformed_hashes(stored_hash):
    assert verify_password("StrongPass123!", stored_hash) is False