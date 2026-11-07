
import math
import time
from typing import Any


def validate_claims(
    payload: dict[str, Any],
    expected_audience: str,
    leeway: int = 0,
) -> dict[str, Any]:
    """Validate required JWT claims after signature verification."""

    if not expected_audience:
        raise ValueError("Expected audience is required")

    if type(leeway) is not int or leeway < 0:
        raise ValueError("Invalid leeway")

    now = time.time()

    # Require all claims for our access-token policy.
    required = ("exp", "iat", "nbf", "jti", "aud")

    for claim in required:
        if claim not in payload:
            raise ValueError(f"Missing claim: {claim}")

    # JWT timestamps are NumericDate values.
    for claim in ("exp", "iat", "nbf"):
        value = payload[claim]

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError(f"Invalid {claim} claim")

    if now >= payload["exp"] + leeway:
        raise ValueError("JWT has expired")

    if payload["iat"] > now + leeway:
        raise ValueError("JWT issued in the future")

    if payload["nbf"] > now + leeway:
        raise ValueError("JWT is not valid yet")

    if payload["exp"] <= payload["iat"]:
        raise ValueError("Invalid JWT lifetime")

    if (
        not isinstance(payload["jti"], str)
        or not payload["jti"]
    ):
        raise ValueError("Invalid JWT ID")

    audience = payload["aud"]

    if isinstance(audience, str):
        valid_audience = audience == expected_audience
    elif isinstance(audience, list):
        valid_audience = (
            bool(audience)
            and all(
                isinstance(item, str) and item
                for item in audience
            )
            and expected_audience in audience
        )
    else:
        valid_audience = False

    if not valid_audience:
        raise ValueError("Invalid JWT audience")

    return payload
