
from django.db.models import (
    Avg,
    Count,
    F,
    Max,
    Min,
    OuterRef,
    Q,
    Subquery,
)

from orm_lab.models import Book, Review


def demonstrate_q_expressions():
    print("\n=== Q EXPRESSIONS ===")

    # OR condition
    books = Book.objects.filter(
        Q(price__lt=310) | Q(stock__gt=80)
    )

    print("Books with price < 310 OR stock > 80:")
    print("Count:", books.count())

    for book in books[:5]:
        print(book.title, book.price, book.stock)

    # AND condition
    books = Book.objects.filter(
        Q(price__gte=310) & Q(stock__gte=20)
    )

    print("\nPrice >= 310 AND stock >= 20:")
    print("Count:", books.count())

    # NOT condition
    books = Book.objects.filter(
        ~Q(stock__lt=50)
    )

    print("\nBooks NOT having stock < 50:")
    print("Count:", books.count())


def demonstrate_f_expressions():
    print("\n=== F EXPRESSIONS ===")

    # Compare two fields in the database
    books = Book.objects.filter(
        stock__gt=F("price") / 5
    )

    print("Books where stock > price / 5:")
    print("Count:", books.count())

    # Database-side arithmetic without modifying records
    books = Book.objects.annotate(
        projected_stock=F("stock") + 10
    )

    print("\nProjected stock after adding 10:")

    for book in books[:5]:
        print(
            book.title,
            "Current:", book.stock,
            "Projected:", book.projected_stock,
        )


def run_advanced_queries():
    demonstrate_q_expressions()
    demonstrate_f_expressions()

def demonstrate_subqueries():
    print("\n=== SUBQUERY AND OUTERREF ===")

    # Find the latest review for each book
    latest_review = (
        Review.objects.filter(
            book_id=OuterRef("pk")
        )
        .order_by("-created_at", "-pk")
    )

    books = Book.objects.annotate(
        latest_reviewer=Subquery(
            latest_review.values("reviewer_name")[:1]
        ),
        latest_rating=Subquery(
            latest_review.values("rating")[:1]
        ),
    )

    print("\nLatest review for each book:")

    for book in books[:5]:
        print(
            book.title,
            "| Reviewer:", book.latest_reviewer,
            "| Rating:", book.latest_rating,
        )


def demonstrate_aggregation():
    print("\n=== AGGREGATION ===")

    statistics = Book.objects.aggregate(
        total_books=Count("id"),
        average_price=Avg("price"),
        minimum_price=Min("price"),
        maximum_price=Max("price"),
    )

    print("\nBook statistics:")

    for key, value in statistics.items():
        print(f"{key}: {value}")

    print("\nReview counts per book:")

    books = Book.objects.annotate(
        total_reviews=Count("reviews")
    )

    for book in books[:5]:
        print(
            book.title,
            "| Reviews:", book.total_reviews,
        )


def run_subquery_aggregation():
    demonstrate_subqueries()
    demonstrate_aggregation()
