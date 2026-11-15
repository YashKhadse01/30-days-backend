
from django.test import TestCase
from django.urls import reverse


class RequestTimingMiddlewareTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/json",
        )

    def test_response_time_header(self):
        response = self.client.get(reverse("health_check"))

        self.assertIn("X-Response-Time-ms", response.headers)

        duration = float(response["X-Response-Time-ms"])
        self.assertGreaterEqual(duration, 0)

    def test_health_response_body(self):
        response = self.client.get(reverse("health_check"))

        data = response.json()
        self.assertEqual(data["status"], "success")
