
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import TOTPDevice

from .jwt_utils import create_access_token
from .refresh_utils import create_refresh_token
from .totp_utils import verify_totp_once


class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        totp_code = request.data.get("totp_code")

        if not isinstance(username, str) or not isinstance(password, str):
            return Response(
                {"detail": "Invalid credentials"},
                status=400,
            )

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is None:
            return Response(
                {"detail": "Invalid credentials"},
                status=401,
            )

        device = TOTPDevice.objects.filter(
            user=user,
            is_verified=True,
        ).first()

        if device is not None and not verify_totp_once(user, totp_code):
            return Response(
                {"detail": "Invalid or missing TOTP code"},
                status=401,
            )

        access_token = create_access_token(user)
        refresh_token, _ = create_refresh_token(user)

        return Response(
            {
                "access": access_token,
                "refresh": refresh_token,
                "token_type": "Bearer",
            }
        )
