
import uuid
from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings
from jwt import InvalidTokenError

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 15
ISSUER = "day23-drf-auth"
AUDIENCE = "day23-api"


def create_access_token(user):
    now = datetime.now(UTC)

    payload = {
        "sub": str(user.pk),
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "iss": ISSUER,
        "aud": AUDIENCE,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_access_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
            options={
                "require": [
                    "sub",
                    "type",
                    "jti",
                    "iat",
                    "nbf",
                    "exp",
                    "iss",
                    "aud",
                ],
            },
        )

        if payload.get("type") != "access":
            raise InvalidTokenError("Invalid token type")

        if not isinstance(payload.get("sub"), str):
            raise InvalidTokenError("Invalid subject")

        return payload

    except InvalidTokenError as exc:
        raise ValueError("Invalid or expired access token") from exc
