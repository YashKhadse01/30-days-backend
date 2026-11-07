
import secrets
import time

import pytest

from jwt_from_scratch.hs256 import sign_hs256
from jwt_from_scratch.rs256 import (
    generate_rsa_key_pair,
    sign_rs256,
)
from jwt_from_scratch.jwt_decoder import decode_jwt
from jwt_from_scratch.revocation import TokenRevocationList


SECRET = "test-only-development-secret"
AUDIENCE = "backend-api"


@pytest.fixture
def payload():
    now = int(time.time())
    return {
        "sub": "user123",
        "iat": now,
        "nbf": now,
        "exp": now + 900,
        "jti": secrets.token_hex(16),
        "aud": AUDIENCE,
    }


@pytest.fixture(scope="module")
def rsa_keys():
    return generate_rsa_key_pair()


@pytest.fixture
def revocation_list():
    return TokenRevocationList()


def test_hs256_complete_verification(payload, revocation_list):
    token = sign_hs256(payload, SECRET)

    result = decode_jwt(
        token,
        algorithm="HS256",
        verification_key=SECRET,
        audience=AUDIENCE,
        revocation_list=revocation_list,
    )

    assert result == payload


def test_rs256_complete_verification(
    payload, rsa_keys, revocation_list
):
    private_key, public_key = rsa_keys
    token = sign_rs256(payload, private_key)

    result = decode_jwt(
        token,
        algorithm="RS256",
        verification_key=public_key,
        audience=AUDIENCE,
        revocation_list=revocation_list,
    )

    assert result == payload


def test_hs256_expired_token_rejected(
    payload, revocation_list
):
    payload["exp"] = payload["iat"] - 10
    token = sign_hs256(payload, SECRET)

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="HS256",
            verification_key=SECRET,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_rs256_wrong_audience_rejected(
    payload, rsa_keys, revocation_list
):
    private_key, public_key = rsa_keys
    token = sign_rs256(payload, private_key)

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="RS256",
            verification_key=public_key,
            audience="another-api",
            revocation_list=revocation_list,
        )


def test_wrong_hs256_secret_rejected(
    payload, revocation_list
):
    token = sign_hs256(payload, SECRET)

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="HS256",
            verification_key="wrong-secret",
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_wrong_rs256_public_key_rejected(
    payload, rsa_keys, revocation_list
):
    private_key, _ = rsa_keys
    token = sign_rs256(payload, private_key)

    _, wrong_public_key = generate_rsa_key_pair()

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="RS256",
            verification_key=wrong_public_key,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_algorithm_confusion_rejected(
    payload, revocation_list
):
    token = sign_hs256(payload, SECRET)
    _, public_key = generate_rsa_key_pair()

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="RS256",
            verification_key=public_key,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_missing_claim_rejected(
    payload, revocation_list
):
    del payload["jti"]
    token = sign_hs256(payload, SECRET)

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="HS256",
            verification_key=SECRET,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_malformed_token_rejected(revocation_list):
    with pytest.raises(ValueError):
        decode_jwt(
            "invalid.jwt.token",
            algorithm="HS256",
            verification_key=SECRET,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_unsupported_algorithm_rejected(
    payload, revocation_list
):
    token = sign_hs256(payload, SECRET)

    with pytest.raises(ValueError):
        decode_jwt(
            token,
            algorithm="none",
            verification_key=SECRET,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_revoked_jwt_rejected(
    payload, revocation_list
):
    token = sign_hs256(payload, SECRET)

    revocation_list.revoke(
        payload["jti"],
        payload["exp"],
    )

    with pytest.raises(ValueError, match="revoked"):
        decode_jwt(
            token,
            algorithm="HS256",
            verification_key=SECRET,
            audience=AUDIENCE,
            revocation_list=revocation_list,
        )


def test_other_jwt_remains_valid(
    payload, revocation_list
):
    revocation_list.revoke(
        payload["jti"],
        payload["exp"],
    )

    second_payload = {
        **payload,
        "jti": secrets.token_hex(16),
    }

    second_token = sign_hs256(second_payload, SECRET)

    result = decode_jwt(
        second_token,
        algorithm="HS256",
        verification_key=SECRET,
        audience=AUDIENCE,
        revocation_list=revocation_list,
    )

    assert result["jti"] == second_payload["jti"]
