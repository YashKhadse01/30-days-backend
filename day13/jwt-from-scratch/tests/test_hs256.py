
import pytest

from jwt_from_scratch.hs256 import (
    sign_hs256,
    verify_hs256,
)


SECRET = "test-only-development-secret"
PAYLOAD = {"sub": "user123", "role": "admin"}


def test_sign_creates_three_segments():
    token = sign_hs256(PAYLOAD, SECRET)
    assert len(token.split(".")) == 3


def test_valid_token_verifies():
    token = sign_hs256(PAYLOAD, SECRET)
    assert verify_hs256(token, SECRET) == PAYLOAD


def test_wrong_secret_rejected():
    token = sign_hs256(PAYLOAD, SECRET)

    with pytest.raises(ValueError):
        verify_hs256(token, "wrong-secret")


def test_tampered_payload_rejected():
    token = sign_hs256(PAYLOAD, SECRET)
    parts = token.split(".")

    # Replace the payload with a differently encoded JSON object.
    from jwt_from_scratch.encoding import json_to_base64url

    parts[1] = json_to_base64url(
        {"sub": "user123", "role": "superadmin"}
    )

    with pytest.raises(ValueError):
        verify_hs256(".".join(parts), SECRET)


def test_malformed_token_rejected():
    with pytest.raises(ValueError):
        verify_hs256("not.a.valid.jwt", SECRET)


def test_empty_signing_secret_rejected():
    with pytest.raises(ValueError):
        sign_hs256(PAYLOAD, "")


def test_empty_verification_secret_rejected():
    token = sign_hs256(PAYLOAD, SECRET)

    with pytest.raises(ValueError):
        verify_hs256(token, "")


def test_wrong_algorithm_rejected():
    from jwt_from_scratch.encoding import json_to_base64url

    token = sign_hs256(PAYLOAD, SECRET)
    parts = token.split(".")

    parts[0] = json_to_base64url(
        {"alg": "none", "typ": "JWT"}
    )

    with pytest.raises(ValueError):
        verify_hs256(".".join(parts), SECRET)
