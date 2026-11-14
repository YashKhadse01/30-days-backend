
from django.contrib import admin

from .models import Author, Book, Category, Publisher, Review


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email")
    search_fields = ("name", "email")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "country")
    search_fields = ("name", "country")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "publisher",
        "price",
        "stock",
        "published_at",
    )

    list_filter = ("publisher", "categories")
    search_fields = ("title", "authors__name")
    filter_horizontal = ("authors", "categories")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "reviewer_name",
        "rating",
        "created_at",
    )

    list_filter = ("rating",)
    search_fields = ("book__title", "reviewer_name")
