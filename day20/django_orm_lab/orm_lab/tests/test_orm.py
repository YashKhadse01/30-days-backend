
from datetime import date
from decimal import Decimal

from django.db.models import Count
from django.test import TestCase

from orm_lab.models import Author, Book, Category, Publisher, Review


class ORMOptimizationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.publisher = Publisher.objects.create(
            name="Test Publisher",
            country="India",
        )

        cls.author = Author.objects.create(
            name="Test Author",
            email="author@example.com",
        )

        cls.category = Category.objects.create(name="Technology")

        for index in range(5):
            book = Book.objects.create(
                title=f"Test Book {index}",
                publisher=cls.publisher,
                price=Decimal("300.00") + index,
                stock=10 + index,
                published_at=date(2026, 11, 1),
            )
            book.authors.add(cls.author)
            book.categories.add(cls.category)

            for rating in (3, 4, 5):
                Review.objects.create(
                    book=book,
                    reviewer_name=f"Reviewer {rating}",
                    rating=rating,
                )

    def test_book_count(self):
        self.assertEqual(Book.objects.count(), 5)

    def test_publisher_select_related(self):
        with self.assertNumQueries(1):
            books = list(Book.objects.select_related("publisher"))
            names = [book.publisher.name for book in books]

        self.assertEqual(len(names), 5)

    def test_authors_prefetch_related(self):
        with self.assertNumQueries(2):
            books = list(Book.objects.prefetch_related("authors"))
            names = [
                author.name
                for book in books
                for author in book.authors.all()
            ]

        self.assertEqual(len(names), 5)

    def test_categories_prefetch_related(self):
        with self.assertNumQueries(2):
            books = list(Book.objects.prefetch_related("categories"))
            names = [
                category.name
                for book in books
                for category in book.categories.all()
            ]

        self.assertEqual(len(names), 5)

    def test_reviews_prefetch_related(self):
        with self.assertNumQueries(2):
            books = list(Book.objects.prefetch_related("reviews"))
            ratings = [
                review.rating
                for book in books
                for review in book.reviews.all()
            ]

        self.assertEqual(len(ratings), 15)

    def test_combined_optimization(self):
        with self.assertNumQueries(4):
            books = list(
                Book.objects.select_related("publisher").prefetch_related(
                    "authors",
                    "categories",
                    "reviews",
                )
            )

            for book in books:
                _ = book.publisher.name
                _ = list(book.authors.all())
                _ = list(book.categories.all())
                _ = list(book.reviews.all())

        self.assertEqual(len(books), 5)

    def test_review_count_annotation(self):
        with self.assertNumQueries(1):
            books = list(
                Book.objects.annotate(
                    review_count=Count("reviews")
                )
            )
            counts = [book.review_count for book in books]

        self.assertEqual(counts, [3] * 5)

    def test_custom_manager_in_stock(self):
        self.assertEqual(Book.objects.in_stock().count(), 5)

    def test_custom_manager_affordable(self):
        self.assertEqual(Book.objects.affordable(302).count(), 3)
