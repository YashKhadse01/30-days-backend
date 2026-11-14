
from datetime import timedelta

from django.db import models
from django.utils import timezone


class BookQuerySet(models.QuerySet):
    def in_stock(self):
        """Return books with available stock."""
        return self.filter(stock__gt=0)

    def affordable(self, max_price=350):
        """Return books within a price limit."""
        return self.filter(price__lte=max_price)

    def recently_published(self, days=30):
        """Return books published within the last N days."""
        cutoff = timezone.localdate() - timedelta(days=days)
        return self.filter(published_at__gte=cutoff)


class BookManager(models.Manager.from_queryset(BookQuerySet)):
    """Custom manager exposing reusable Book queries."""