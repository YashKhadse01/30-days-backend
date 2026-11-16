
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient


class BookThrottleTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        self.url = "/api/v1/books/"

    def tearDown(self):
        cache.clear()

    def test_anonymous_rate_limit(self):
        for _ in range(5):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 429)
