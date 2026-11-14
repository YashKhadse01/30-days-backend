
from django.db import models

from .managers import BookManager


class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Publisher(models.Model):
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)

    authors = models.ManyToManyField(
        Author,
        related_name="books",
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name="books",
    )

    categories = models.ManyToManyField(
        Category,
        related_name="books",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    stock = models.PositiveIntegerField(default=0)

    published_at = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # Custom manager for reusable ORM queries
    objects = BookManager()

    def __str__(self):
        return self.title


class Review(models.Model):
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    reviewer_name = models.CharField(max_length=100)

    rating = models.PositiveSmallIntegerField()

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.book.title} - {self.rating}/5"
