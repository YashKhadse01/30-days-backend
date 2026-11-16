
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Author, Book


class BookPermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.author = Author.objects.create(
            name="Test Author",
            email="testauthor@example.com",
        )

        self.book = Book.objects.create(
            title="Test Book",
            author=self.author,
            price="299.00",
        )

        user_model = get_user_model()

        self.regular_user = user_model.objects.create_user(
            username="regular",
            password="TestPassword123!",
        )

        self.staff_user = user_model.objects.create_user(
            username="staff",
            password="TestPassword123!",
            is_staff=True,
        )

        self.url = "/api/v1/books/"

    def test_anonymous_user_can_read_books(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_cannot_create_book(self):
        response = self.client.post(
            self.url,
            {
                "title": "Unauthorized Book",
                "author": self.author.id,
                "price": "199.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(
            user=self.regular_user
        )

        response = self.client.post(
            self.url,
            {
                "title": "Regular User Book",
                "author": self.author.id,
                "price": "199.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_create_book(self):
        self.client.force_authenticate(
            user=self.staff_user
        )

        response = self.client.post(
            self.url,
            {
                "title": "Staff Created Book",
                "author": self.author.id,
                "price": "499.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Book.objects.filter(
                title="Staff Created Book"
            ).exists()
        )
