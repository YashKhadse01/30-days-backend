
from django.db import connection
from django.db.models import Count
from django.test.utils import CaptureQueriesContext

from orm_lab.models import Book


def run_experiment(label, queryset):
    with CaptureQueriesContext(connection) as queries:
        results = [
            {
                "title": book.title,
                "publisher": book.publisher.name,
            }
            for book in queryset
        ]

    print(f"\n{label}")
    print(f"Books processed: {len(results)}")
    print(f"SQL queries executed: {len(queries)}")

    return len(queries)


def compare_publisher_queries():
    print("=" * 50)
    print("EXPERIMENT 1: ForeignKey N+1 Problem")
    print("=" * 50)

    without_optimization = run_experiment(
        "WITHOUT select_related()",
        Book.objects.all(),
    )

    with_optimization = run_experiment(
        "WITH select_related()",
        Book.objects.select_related("publisher"),
    )

    print("\nRESULTS")
    print(f"Before: {without_optimization} queries")
    print(f"After: {with_optimization} queries")
    print(
        f"Queries saved: "
        f"{without_optimization - with_optimization}"
    )

def run_author_experiment(label, queryset):
    with CaptureQueriesContext(connection) as queries:
        results = [
            {
                "title": book.title,
                "authors": [
                    author.name
                    for author in book.authors.all()
                ],
            }
            for book in queryset
        ]

    print(f"\n{label}")
    print(f"Books processed: {len(results)}")
    print(f"SQL queries executed: {len(queries)}")

    return len(queries)


def compare_author_queries():
    print("=" * 50)
    print("EXPERIMENT 2: ManyToMany N+1 Problem")
    print("=" * 50)

    before = run_author_experiment(
        "WITHOUT prefetch_related()",
        Book.objects.all(),
    )

    after = run_author_experiment(
        "WITH prefetch_related()",
        Book.objects.prefetch_related("authors"),
    )

    print("\nRESULTS")
    print(f"Before: {before} queries")
    print(f"After: {after} queries")
    print(f"Queries saved: {before - after}")

def run_review_experiment(label, queryset):
    with CaptureQueriesContext(connection) as queries:
        results = [
            {
                "title": book.title,
                "reviews": [
                    {
                        "reviewer": review.reviewer_name,
                        "rating": review.rating,
                    }
                    for review in book.reviews.all()
                ],
            }
            for book in queryset
        ]

    print(f"\n{label}")
    print(f"Books processed: {len(results)}")
    print(f"SQL queries executed: {len(queries)}")

    return len(queries)


def compare_review_queries():
    print("=" * 50)
    print("EXPERIMENT 3: Reverse ForeignKey N+1 Problem")
    print("=" * 50)

    before = run_review_experiment(
        "WITHOUT prefetch_related()",
        Book.objects.all(),
    )

    after = run_review_experiment(
        "WITH prefetch_related()",
        Book.objects.prefetch_related("reviews"),
    )

    print("\nRESULTS")
    print(f"Before: {before} queries")
    print(f"After: {after} queries")
    print(f"Queries saved: {before - after}")

def run_combined_experiment(label, queryset):
    with CaptureQueriesContext(connection) as queries:
        results = []

        for book in queryset:
            results.append(
                {
                    "title": book.title,
                    "publisher": book.publisher.name,
                    "authors": [
                        author.name
                        for author in book.authors.all()
                    ],
                    "categories": [
                        category.name
                        for category in book.categories.all()
                    ],
                    "reviews": [
                        review.rating
                        for review in book.reviews.all()
                    ],
                }
            )

    print(f"\n{label}")
    print(f"Books processed: {len(results)}")
    print(f"SQL queries executed: {len(queries)}")

    return len(queries)


def compare_combined_queries():
    print("=" * 50)
    print("EXPERIMENT 4: Multiple Relationship N+1")
    print("=" * 50)

    before = run_combined_experiment(
        "WITHOUT optimization",
        Book.objects.all(),
    )

    after = run_combined_experiment(
        "WITH combined optimization",
        Book.objects.select_related(
            "publisher"
        ).prefetch_related(
            "authors",
            "categories",
            "reviews",
        ),
    )

    print("\nRESULTS")
    print(f"Before: {before} queries")
    print(f"After: {after} queries")
    print(f"Queries saved: {before - after}")

def compare_review_count_queries():
    print("=" * 50)
    print("EXPERIMENT 5: Review Count N+1 Problem")
    print("=" * 50)

    with CaptureQueriesContext(connection) as queries:
        before_results = [
            {
                "title": book.title,
                "review_count": book.reviews.count(),
            }
            for book in Book.objects.all()
        ]

    before = len(queries)

    print("\nWITHOUT annotate()")
    print(f"Books processed: {len(before_results)}")
    print(f"SQL queries executed: {before}")

    with CaptureQueriesContext(connection) as queries:
        after_results = [
            {
                "title": book.title,
                "review_count": book.review_count,
            }
            for book in Book.objects.annotate(
                review_count=Count("reviews")
            )
        ]

    after = len(queries)

    print("\nWITH annotate() and Count()")
    print(f"Books processed: {len(after_results)}")
    print(f"SQL queries executed: {after}")

    assert sorted(
        (item["title"], item["review_count"])
        for item in before_results
    ) == sorted(
        (item["title"], item["review_count"])
        for item in after_results
    )

    print("\nRESULTS")
    print(f"Before: {before} queries")
    print(f"After: {after} queries")
    print(f"Queries saved: {before - after}")
    print("Review counts verified successfully!")
