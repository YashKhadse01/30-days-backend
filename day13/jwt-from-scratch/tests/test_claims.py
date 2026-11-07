
import secrets
import time

import pytest

from jwt_from_scratch.claims import validate_claims


AUDIENCE = "backend-api"


@pytest.fixture
def valid_payload():
    now = int(time.time())

    return {
        "sub": "user123",
        "iat": now,
        "nbf": now,
        "exp": now + 900,
        "jti": secrets.token_hex(16),
        "aud": AUDIENCE,
    }


def test_valid_claims_accepted(valid_payload):
    result = validate_claims(valid_payload, AUDIENCE)
    assert result["sub"] == "user123"


def test_expired_token_rejected(valid_payload):
    valid_payload["exp"] = valid_payload["iat"] - 10

    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE)


def test_future_issued_token_rejected(valid_payload):
    valid_payload["iat"] += 3600

    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE)


def test_future_nbf_rejected(valid_payload):
    valid_payload["nbf"] += 3600

    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE)


def test_wrong_audience_rejected(valid_payload):
    with pytest.raises(ValueError):
        validate_claims(valid_payload, "other-api")


def test_audience_list_accepted(valid_payload):
    valid_payload["aud"] = ["backend-api", "admin-api"]

    assert validate_claims(valid_payload, AUDIENCE)


def test_missing_claim_rejected(valid_payload):
    del valid_payload["jti"]

    with pytest.raises(ValueError, match="Missing claim"):
        validate_claims(valid_payload, AUDIENCE)


def test_empty_jti_rejected(valid_payload):
    valid_payload["jti"] = ""

    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE)


@pytest.mark.parametrize(
    "invalid_value",
    [True, "tomorrow", None, float("nan"), float("inf")],
)
def test_invalid_exp_type_rejected(valid_payload, invalid_value):
    valid_payload["exp"] = invalid_value

    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE)


def test_invalid_lifetime_rejected(valid_payload):
    valid_payload["exp"] = valid_payload["iat"]

    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE)


def test_negative_leeway_rejected(valid_payload):
    with pytest.raises(ValueError):
        validate_claims(valid_payload, AUDIENCE, leeway=-1)


def test_missing_expected_audience_rejected(valid_payload):
    with pytest.raises(ValueError):
        validate_claims(valid_payload, "")
