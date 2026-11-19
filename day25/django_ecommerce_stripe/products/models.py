from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(price__gt=0),
                name="product_price_positive",
            ),
            models.CheckConstraint(
                condition=Q(stock__gte=0),
                name="product_stock_nonnegative",
            ),
        ]

    def __str__(self):
        return self.name