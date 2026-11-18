
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from webhooks.models import WebhookEndpoint


class WebhookEndpointAPITests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.admin_user = user_model.objects.create_user(
            username="webhook_admin",
            password="test-admin-password",
            is_staff=True,
        )

        self.normal_user = user_model.objects.create_user(
            username="webhook_user",
            password="test-user-password",
        )

        self.client = APIClient()
        self.url = "/api/webhooks/endpoints/"

        self.valid_payload = {
            "url": "https://example.com/webhook/",
            "secret": "development-test-secret-123",
            "is_active": True,
        }

    def test_admin_can_create_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(WebhookEndpoint.objects.count(), 1)

    def test_unauthenticated_user_cannot_create(self):
        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(WebhookEndpoint.objects.count(), 0)

    def test_non_admin_cannot_create(self):
        self.client.force_authenticate(user=self.normal_user)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(WebhookEndpoint.objects.count(), 0)

    def test_secret_not_returned_in_response(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.url,
            self.valid_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertNotIn("secret", response.data)

        list_response = self.client.get(self.url)

        self.assertEqual(list_response.status_code, 200)
        self.assertNotIn("secret", list_response.data[0])

    def test_invalid_url_rejected(self):
        self.client.force_authenticate(user=self.admin_user)

        payload = {
            **self.valid_payload,
            "url": "http://example.com/webhook/",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(WebhookEndpoint.objects.count(), 0)
