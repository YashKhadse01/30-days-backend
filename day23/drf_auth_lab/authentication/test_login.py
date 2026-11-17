
import pyotp
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import TOTPDevice


class LoginIntegrationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="login_test_user",
            password="StrongTestPassword123!",
        )
        self.client = APIClient()
        self.url = "/api/login/"
        self.credentials = {
            "username": "login_test_user",
            "password": "StrongTestPassword123!",
        }

    def test_login_without_2fa(self):
        response = self.client.post(
            self.url,
            self.credentials,
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_wrong_password(self):
        response = self.client.post(
            self.url,
            {
                **self.credentials,
                "password": "wrong-password",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_2fa_requires_code(self):
        TOTPDevice.objects.create(
            user=self.user,
            secret=pyotp.random_base32(),
            is_verified=True,
        )

        response = self.client.post(
            self.url,
            self.credentials,
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_2fa_valid_code(self):
        secret = pyotp.random_base32()
        TOTPDevice.objects.create(
            user=self.user,
            secret=secret,
            is_verified=True,
        )

        response = self.client.post(
            self.url,
            {
                **self.credentials,
                "totp_code": pyotp.TOTP(secret).now(),
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_2fa_code_replay_rejected(self):
        secret = pyotp.random_base32()
        TOTPDevice.objects.create(
            user=self.user,
            secret=secret,
            is_verified=True,
        )

        payload = {
            **self.credentials,
            "totp_code": pyotp.TOTP(secret).now(),
        }

        first = self.client.post(
            self.url, payload, format="json"
        )
        second = self.client.post(
            self.url, payload, format="json"
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 401)
