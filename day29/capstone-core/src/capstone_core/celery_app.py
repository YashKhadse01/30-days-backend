"""Redis-backed Celery application."""

from celery import Celery

from capstone_core.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "capstone_core",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["capstone_core.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_time_limit=120,
)
