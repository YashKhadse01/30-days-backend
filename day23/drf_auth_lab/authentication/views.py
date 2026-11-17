
from rest_framework.response import Response
from rest_framework.views import APIView


class ProfileView(APIView):
    def get(self, request):
        return Response(
            {
                "message": "JWT authentication successful",
                "user_id": request.user.pk,
                "username": request.user.username,
            }
        )
