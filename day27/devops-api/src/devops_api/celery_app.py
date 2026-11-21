from celery import Celery

from devops_api.config import get_settings

settings = get_settings()

celery_app = Celery(
    "devops_api",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["devops_api.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
