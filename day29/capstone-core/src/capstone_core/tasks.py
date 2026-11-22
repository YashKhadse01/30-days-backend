"""Background tasks for the capstone application."""

from capstone_core.celery_app import celery_app


@celery_app.task(name="capstone_core.process_report")
def process_report(report_id: str) -> dict[str, str]:
    """Process a report asynchronously through a Celery worker."""
    if not report_id.strip():
        raise ValueError("Report ID cannot be empty")

    return {
        "report_id": report_id,
        "status": "processed",
    }
