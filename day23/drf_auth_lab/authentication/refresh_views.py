
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .jwt_utils import create_access_token
from .refresh_utils import rotate_refresh_token


class RefreshTokenView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not isinstance(refresh_token, str) or not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=400,
            )

        try:
            new_refresh_token, user = rotate_refresh_token(
                refresh_token
            )
        except ValueError:
            return Response(
                {"detail": "Invalid or expired refresh token"},
                status=401,
            )

        access_token = create_access_token(user)

        return Response(
            {
                "access": access_token,
                "refresh": new_refresh_token,
                "token_type": "Bearer",
            }
        )
