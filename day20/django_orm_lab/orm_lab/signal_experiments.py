
from unittest.mock import patch

from orm_lab.models import Book, Review


def demonstrate_signals():
    print("\n=== DJANGO SIGNAL EXPERIMENT ===")

    book = Book.objects.first()

    if book is None:
        print("No books found. Run seed_data first.")
        return

    with (
        patch("orm_lab.signals.review_saved") as _unused,
    ):
        pass

    # Observe the actual logging calls from signal handlers.
    with patch("orm_lab.signals.logger") as mock_logger:
        review = Review.objects.create(
            book=book,
            reviewer_name="Signal Test Reviewer",
            rating=5,
            comment="Testing Django signals",
        )

        print("Review created:", review.pk)
        print(
            "post_save on create:",
            mock_logger.info.call_count == 1,
        )

        mock_logger.reset_mock()

        review.rating = 4
        review.save()

        print(
            "post_save on update:",
            mock_logger.info.call_count == 1,
        )

        mock_logger.reset_mock()

        review.delete()

        print(
            "post_delete on delete:",
            mock_logger.info.call_count == 1,
        )

    print("Signal experiment completed!")
