
from django.test import TestCase
from rest_framework.test import APIClient


class BookVersioningTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_v1_books_endpoint(self):
        response = self.client.get("/api/v1/books/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.wsgi_request.path, "/api/v1/books/")

    def test_unsupported_version(self):
        response = self.client.get("/api/v2/books/")

        self.assertEqual(response.status_code, 404)
