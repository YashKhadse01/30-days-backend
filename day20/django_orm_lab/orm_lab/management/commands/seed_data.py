
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from orm_lab.models import Author, Book, Category, Publisher, Review


class Command(BaseCommand):
    help = "Generate sample records for Django ORM experiments"

    @transaction.atomic
    def handle(self, *args, **options):
        authors = []
        publishers = []
        categories = []

        for i in range(1, 11):
            author, _ = Author.objects.get_or_create(
                email=f"author{i}@example.com",
                defaults={"name": f"Author {i}"},
            )
            authors.append(author)

        for i in range(1, 6):
            publisher, _ = Publisher.objects.get_or_create(
                name=f"Publisher {i}",
                defaults={"country": "India"},
            )
            publishers.append(publisher)

        for name in [
            "Technology",
            "Science",
            "Business",
            "Fiction",
            "Education",
        ]:
            category, _ = Category.objects.get_or_create(
                name=name
            )
            categories.append(category)

        for i in range(1, 51):
            book, created = Book.objects.get_or_create(
                title=f"Django ORM Book {i}",
                defaults={
                    "publisher": publishers[(i - 1) % 5],
                    "price": Decimal("299.00") + i,
                    "stock": i * 2,
                    "published_at": date.today()
                    - timedelta(days=i),
                },
            )

            if created:
                book.authors.add(
                    authors[(i - 1) % 10],
                    authors[i % 10],
                )

                book.categories.add(
                    categories[(i - 1) % 5],
                    categories[i % 5],
                )

            for j in range(1, 4):
                Review.objects.get_or_create(
                    book=book,
                    reviewer_name=f"Reviewer {j}",
                    defaults={
                        "rating": (i + j) % 5 + 1,
                        "comment": f"Review {j} for book {i}",
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Sample database generated successfully!"
            )
        )
