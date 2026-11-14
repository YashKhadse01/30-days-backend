
from django.db import connection, transaction
from django.db.models import F

from orm_lab.models import Book


def demonstrate_transaction():
    print("\n=== DATABASE TRANSACTION EXPERIMENT ===")

    book = Book.objects.order_by("id").first()

    if book is None:
        print("No books found. Run seed_data first.")
        return

    original_stock = book.stock

    print("Book:", book.title)
    print("Original stock:", original_stock)
    print("Database:", connection.vendor)

    # Use a transaction to group operations.
    with transaction.atomic():
        locked_book = (
            Book.objects.select_for_update()
            .get(pk=book.pk)
        )

        if locked_book.stock <= 0:
            print("Insufficient stock.")
            return

        Book.objects.filter(
            pk=locked_book.pk,
            stock__gt=0,
        ).update(stock=F("stock") - 1)

        print("Stock decremented inside transaction.")

    book.refresh_from_db()
    print("Updated stock:", book.stock)

    # Restore the original stock for repeatable experiments.
    with transaction.atomic():
        Book.objects.filter(pk=book.pk).update(
            stock=original_stock
        )

    book.refresh_from_db()
    print("Restored stock:", book.stock)
    print("Experiment completed successfully!")
