
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Author, Book
from .permissions import IsStaffOrReadOnly
from .serializers import AuthorSerializer, BookSerializer
from .throttles import BookAnonThrottle, BookUserThrottle


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by("id")
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "email"]


class BookViewSet(viewsets.ModelViewSet):
    queryset = (
        Book.objects.select_related("author")
        .prefetch_related("reviews")
        .order_by("id")
    )
    serializer_class = BookSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = ["author"]
    search_fields = ["title", "description", "author__name"]
    ordering_fields = ["price", "created_at", "title"]
    ordering = ["id"]
    permission_classes = [IsStaffOrReadOnly]
    throttle_classes = [BookAnonThrottle, BookUserThrottle]