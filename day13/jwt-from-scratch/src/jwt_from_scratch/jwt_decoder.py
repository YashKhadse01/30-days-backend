
from typing import Any

from jwt_from_scratch.claims import validate_claims
from jwt_from_scratch.hs256 import verify_hs256
from jwt_from_scratch.rs256 import verify_rs256
from jwt_from_scratch.revocation import TokenRevocationList


def decode_jwt(
    token: str,
    *,
    algorithm: str,
    verification_key: Any,
    audience: str,
    revocation_list: TokenRevocationList,
    leeway: int = 0,
) -> dict[str, Any]:
    """Verify signature, claims, and token revocation."""

    if algorithm == "HS256":
        if not isinstance(verification_key, str):
            raise ValueError("HS256 requires a string secret")

        payload = verify_hs256(token, verification_key)

    elif algorithm == "RS256":
        payload = verify_rs256(token, verification_key)

    else:
        raise ValueError("Unsupported JWT algorithm")

    validated_payload = validate_claims(
        payload=payload,
        expected_audience=audience,
        leeway=leeway,
    )

    jti = validated_payload["jti"]

    if revocation_list.is_revoked(jti):
        raise ValueError("JWT has been revoked")

    return validated_payload
