
from django.http import HttpResponse

from orm_lab.models import Book


def book_performance_view(request):
    optimized = request.GET.get("optimized") == "1"

    books = Book.objects.order_by("id")

    if optimized:
        books = books.select_related(
            "publisher"
        ).prefetch_related(
            "authors",
            "categories",
            "reviews",
        )

    rows = []

    for book in books:
        publisher = book.publisher.name
        authors = ", ".join(
            author.name for author in book.authors.all()
        )
        categories = ", ".join(
            category.name for category in book.categories.all()
        )
        review_count = len(book.reviews.all())

        rows.append(
            "<tr>"
            f"<td>{book.pk}</td>"
            f"<td>{book.title}</td>"
            f"<td>{publisher}</td>"
            f"<td>{authors}</td>"
            f"<td>{categories}</td>"
            f"<td>{review_count}</td>"
            "</tr>"
        )

    mode = "Optimized" if optimized else "Unoptimized"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Django ORM Performance</title>
    </head>
    <body>
        <h1>Django ORM Performance - {mode}</h1>
        <p>
            <a href="?optimized=0">Unoptimized</a> |
            <a href="?optimized=1">Optimized</a>
        </p>
        <table border="1" cellpadding="8">
            <tr>
                <th>ID</th>
                <th>Book</th>
                <th>Publisher</th>
                <th>Authors</th>
                <th>Categories</th>
                <th>Reviews</th>
            </tr>
            {"".join(rows)}
        </table>
    </body>
    </html>
    """

    return HttpResponse(html)
