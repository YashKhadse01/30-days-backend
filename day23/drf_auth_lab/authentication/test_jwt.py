
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authentication.jwt_utils import create_access_token


class JWTAuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="jwt_test",
            password="StrongTestPassword123!",
        )
        self.client = APIClient()
        self.url = "/api/profile/"

    def test_valid_token(self):
        token = create_access_token(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["username"],
            "jwt_test",
        )

    def test_missing_token(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_invalid_token(self):
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid.token.value"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_disabled_user(self):
        self.user.is_active = False
        self.user.save()

        token = create_access_token(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
