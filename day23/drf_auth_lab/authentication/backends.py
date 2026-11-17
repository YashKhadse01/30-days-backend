
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .jwt_utils import verify_access_token


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.headers.get("Authorization", "")

        if not header:
            return None

        parts = header.split()

        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise AuthenticationFailed(
                "Invalid Authorization header"
            )

        try:
            payload = verify_access_token(parts[1])
        except ValueError as exc:
            raise AuthenticationFailed(
                "Invalid or expired access token"
            ) from exc

        User = get_user_model()

        try:
            user = User.objects.get(pk=payload["sub"])
        except (User.DoesNotExist, ValueError, TypeError) as exc:
            raise AuthenticationFailed(
                "User not found"
            ) from exc

        if not user.is_active:
            raise AuthenticationFailed(
                "User account is disabled"
            )

        return user, payload

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
