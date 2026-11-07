
import pytest
from jwt_from_scratch.encoding import base64url_encode
from jwt_from_scratch.encoding import json_to_base64url
from jwt_from_scratch.rs256 import (
    generate_rsa_key_pair,
    sign_rs256,
    verify_rs256,
)


@pytest.fixture(scope="module")
def rsa_keys():
    return generate_rsa_key_pair()


@pytest.fixture
def signed_token(rsa_keys):
    private_key, _ = rsa_keys
    return sign_rs256(
        {"sub": "user123", "role": "admin"},
        private_key,
    )


def test_rs256_creates_three_segments(signed_token):
    assert len(signed_token.split(".")) == 3


def test_rs256_valid_signature(signed_token, rsa_keys):
    _, public_key = rsa_keys

    payload = verify_rs256(signed_token, public_key)

    assert payload["sub"] == "user123"
    assert payload["role"] == "admin"


def test_rs256_wrong_public_key_rejected(signed_token):
    _, wrong_public_key = generate_rsa_key_pair()

    with pytest.raises(ValueError):
        verify_rs256(signed_token, wrong_public_key)


def test_rs256_tampered_payload_rejected(signed_token, rsa_keys):
    _, public_key = rsa_keys

    parts = signed_token.split(".")
    parts[1] = json_to_base64url(
        {"sub": "attacker", "role": "admin"}
    )

    with pytest.raises(ValueError):
        verify_rs256(".".join(parts), public_key)


def test_rs256_none_algorithm_rejected(signed_token, rsa_keys):
    _, public_key = rsa_keys

    parts = signed_token.split(".")
    parts[0] = json_to_base64url(
        {"alg": "none", "typ": "JWT"}
    )

    with pytest.raises(ValueError):
        verify_rs256(".".join(parts), public_key)


def test_rs256_malformed_token_rejected(rsa_keys):
    _, public_key = rsa_keys

    with pytest.raises(ValueError):
        verify_rs256("invalid.jwt", public_key)


def test_rs256_wrong_signature_rejected(signed_token, rsa_keys):
    _, public_key = rsa_keys

    parts = signed_token.split(".")
    parts[2] = base64url_encode(b"fake-signature")

    with pytest.raises(ValueError):
        verify_rs256(".".join(parts), public_key)


def test_rs256_different_keys_generate_different_signatures():
    private_key_1, _ = generate_rsa_key_pair()
    private_key_2, _ = generate_rsa_key_pair()

    payload = {"sub": "user123"}

    token_1 = sign_rs256(payload, private_key_1)
    token_2 = sign_rs256(payload, private_key_2)

    assert token_1 != token_2
