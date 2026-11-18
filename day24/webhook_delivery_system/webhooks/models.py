
import uuid
from typing import ClassVar

from django.db import models


class WebhookEndpoint(models.Model):
    url = models.URLField(max_length=2048)
    secret = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url


class WebhookEvent(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type}: {self.id}"


class WebhookDelivery(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCESS = "success", "Success"
        RETRYING = "retrying", "Retrying"
        FAILED = "failed", "Failed"

    event = models.ForeignKey(
        WebhookEvent,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name="deliveries",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    attempts = models.PositiveIntegerField(default=0)
    last_status_code = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    last_error = models.TextField(blank=True)
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints: ClassVar[list] = [
            models.UniqueConstraint(
                fields=["event", "endpoint"],
                name="unique_webhook_event_endpoint",
            )
        ]

    def __str__(self):
        return f"{self.event.event_type} -> {self.endpoint.url}"

class WebhookDeliveryAttempt(models.Model):
    delivery = models.ForeignKey(
        WebhookDelivery,
        on_delete=models.CASCADE,
        related_name="attempt_logs",
    )

    attempt_number = models.PositiveIntegerField()

    status_code = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    succeeded = models.BooleanField(default=False)

    error_message = models.TextField(blank=True)

    attempted_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering : ClassVar[list[str]] = ["attempt_number"]
        constraints : ClassVar[list] = [
            models.UniqueConstraint(
                fields=["delivery", "attempt_number"],
                name="unique_webhook_delivery_attempt",
            )
        ]

    def __str__(self):
        return (
            f"Delivery {self.delivery_id} "
            f"- Attempt {self.attempt_number}"
        )
