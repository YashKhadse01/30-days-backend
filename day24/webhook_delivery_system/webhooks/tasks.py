import logging

import requests
from celery import shared_task
from django.db import models, transaction
from django.utils import timezone

from webhooks.delivery import send_webhook
from webhooks.models import WebhookDelivery, WebhookDeliveryAttempt


@shared_task
def test_celery_connection():
    return {
        "status": "success",
        "message": "Django, Celery and Redis are connected",
    }

@shared_task(bind=True, max_retries=3)
def test_retry_task(self, attempt_failures: int = 2):
    """Simulate transient failures before successful processing."""

    if not 0 <= attempt_failures <= 3:
        raise ValueError("attempt_failures must be between 0 and 3")

    attempt = self.request.retries + 1

    if self.request.retries < attempt_failures:
        delay = min(2 ** self.request.retries, 8)

        raise self.retry(
            exc=RuntimeError("Simulated temporary failure"),
            countdown=delay,
        )

    return {
        "status": "success",
        "attempts": attempt,
        "message": "Task completed after transient failures",
    }

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 4

@shared_task(bind=True, max_retries=3)
def deliver_webhook(self, delivery_id: int):
    """Deliver a webhook with bounded retries and attempt logs."""

    with transaction.atomic():
        delivery = (
            WebhookDelivery.objects.select_for_update()
            .select_related("event", "endpoint")
            .get(pk=delivery_id)
        )

        if delivery.status == WebhookDelivery.Status.SUCCESS:
            return {"status": "already_delivered"}

        if delivery.status == WebhookDelivery.Status.FAILED:
            return {"status": "already_failed"}

        if delivery.status == WebhookDelivery.Status.PROCESSING:
            return {"status": "already_processing"}

        if not delivery.endpoint.is_active:
            delivery.status = WebhookDelivery.Status.FAILED
            delivery.last_error = "Endpoint is inactive"
            delivery.save(
                update_fields=["status", "last_error", "updated_at"]
            )
            return {"status": "failed", "reason": "inactive_endpoint"}

        if delivery.attempts >= MAX_ATTEMPTS:
            delivery.status = WebhookDelivery.Status.FAILED
            delivery.last_error = "Maximum attempts reached"
            delivery.save(
                update_fields=["status", "last_error", "updated_at"]
            )
            return {"status": "failed", "reason": "max_attempts"}

        delivery.attempts += 1
        attempt_number = delivery.attempts
        delivery.status = WebhookDelivery.Status.PROCESSING
        delivery.save(
            update_fields=["attempts", "status", "updated_at"]
        )

    status_code = None
    error_message = ""

    try:
        response = send_webhook(
            url=delivery.endpoint.url,
            secret=delivery.endpoint.secret,
            event_id=str(delivery.event.id),
            event_type=delivery.event.event_type,
            payload=delivery.event.payload,
        )
        status_code = response.status_code
        succeeded = 200 <= status_code < 300

        if not succeeded:
            error_message = f"Receiver returned HTTP {status_code}"

    except requests.RequestException as exc:
        succeeded = False
        error_message = str(exc)

    WebhookDeliveryAttempt.objects.create(
        delivery_id=delivery_id,
        attempt_number=attempt_number,
        status_code=status_code,
        succeeded=succeeded,
        error_message=error_message,
    )

    delivery.refresh_from_db()
    delivery.last_status_code = status_code
    delivery.last_error = error_message

    if succeeded:
        delivery.status = WebhookDelivery.Status.SUCCESS
        delivery.delivered_at = timezone.now()
    else:
        retryable = (
            status_code is None
            or status_code in (408, 425, 429)
            or (status_code is not None and status_code >= 500)
        )

        if retryable and attempt_number < MAX_ATTEMPTS:
            delivery.status = WebhookDelivery.Status.RETRYING
        else:
            delivery.status = WebhookDelivery.Status.FAILED

    delivery.save(
        update_fields=[
            "status",
            "last_status_code",
            "last_error",
            "delivered_at",
            "updated_at",
        ]
    )

    if delivery.status == WebhookDelivery.Status.RETRYING:
        delay = min(2 ** (attempt_number - 1), 60)

        logger.warning(
            "Webhook delivery %s failed on attempt %s; "
            "retrying in %s seconds",
            delivery_id,
            attempt_number,
            delay,
        )

        raise self.retry(
            exc=RuntimeError(error_message),
            countdown=delay,
        )

    return {
        "status": delivery.status,
        "http_status": status_code,
        "attempts": attempt_number,
    }

@shared_task
def monitor_webhook_deliveries():
    """Return a summary of webhook delivery statuses."""

    statuses = (
        WebhookDelivery.objects.values("status")
        .annotate(total=models.Count("id"))
        .order_by("status")
    )

    summary = {
        item["status"]: item["total"]
        for item in statuses
    }

    logger.info("Webhook delivery summary: %s", summary)

    return summary
