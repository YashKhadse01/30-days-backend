
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import RefreshToken
from authentication.refresh_utils import hash_refresh_token


class RefreshAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="refresh_api_user",
            password="StrongTestPassword123!",
        )
        self.client = APIClient()
        self.login_url = "/api/login/"
        self.refresh_url = "/api/refresh/"

        response = self.client.post(
            self.login_url,
            {
                "username": "refresh_api_user",
                "password": "StrongTestPassword123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.original_refresh = response.data["refresh"]

    def test_refresh_success(self):
        response = self.client.post(
            self.refresh_url,
            {"refresh": self.original_refresh},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertNotEqual(
            self.original_refresh,
            response.data["refresh"],
        )

    def test_missing_refresh_token(self):
        response = self.client.post(
            self.refresh_url, {}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_refresh_token(self):
        response = self.client.post(
            self.refresh_url,
            {"refresh": "invalid-token"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_reuse_revokes_token_family(self):
        first = self.client.post(
            self.refresh_url,
            {"refresh": self.original_refresh},
            format="json",
        )
        self.assertEqual(first.status_code, 200)

        replacement = first.data["refresh"]

        reuse = self.client.post(
            self.refresh_url,
            {"refresh": self.original_refresh},
            format="json",
        )
        self.assertEqual(reuse.status_code, 401)

        record = RefreshToken.objects.get(
            token_hash=hash_refresh_token(replacement)
        )
        record.refresh_from_db()
        self.assertIsNotNone(record.revoked_at)

        blocked = self.client.post(
            self.refresh_url,
            {"refresh": replacement},
            format="json",
        )
        self.assertEqual(blocked.status_code, 401)

    def test_disabled_user_cannot_refresh(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            self.refresh_url,
            {"refresh": self.original_refresh},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
