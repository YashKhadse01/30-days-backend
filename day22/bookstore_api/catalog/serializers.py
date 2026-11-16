
from django.db import transaction
from rest_framework import serializers

from reviews.models import Review
from reviews.serializers import ReviewSerializer

from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name", "email"]
        read_only_fields = ["id"]


class BookSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, required=False)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "description",
            "author",
            "price",
            "created_at",
            "reviews",
        ]
        read_only_fields = ["id", "created_at"]

    @transaction.atomic
    def create(self, validated_data):
        reviews_data = validated_data.pop("reviews", [])

        book = Book.objects.create(**validated_data)

        for review_data in reviews_data:
            Review.objects.create(
                book=book,
                **review_data,
            )

        return book

    @transaction.atomic
    def update(self, instance, validated_data):
        reviews_data = validated_data.pop("reviews", None)

        for attribute, value in validated_data.items():
            setattr(instance, attribute, value)

        instance.save()

        if reviews_data is not None:
            instance.reviews.all().delete()

            for review_data in reviews_data:
                Review.objects.create(
                    book=instance,
                    **review_data,
                )

        return instance
