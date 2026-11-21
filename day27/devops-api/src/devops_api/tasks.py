import logging

from sqlalchemy import create_engine, update
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from devops_api.celery_app import celery_app
from devops_api.config import get_settings
from devops_api.models import Task

logger = logging.getLogger(__name__)

settings = get_settings()

# Celery workers use a synchronous PostgreSQL connection.
sync_database_url = make_url(settings.database_url).set(drivername="postgresql+psycopg")

engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
)


@celery_app.task(name="devops_api.process_task")
def process_task(task_id: int) -> dict[str, int | str]:
    """Process a database task in the background."""

    with Session(engine) as session:
        task = session.get(Task, task_id)

        if task is None:
            logger.warning("Task %s not found", task_id)
            return {
                "task_id": task_id,
                "status": "not_found",
            }

        task.status = "processing"
        session.commit()

        try:
            # Placeholder for real background processing.
            logger.info("Processing task %s", task_id)

            task.status = "completed"
            session.commit()

            return {
                "task_id": task_id,
                "status": "completed",
            }

        except Exception:
            session.rollback()

            session.execute(
                update(Task).where(Task.id == task_id).values(status="failed")
            )
            session.commit()

            logger.exception(
                "Background processing failed for task %s",
                task_id,
            )
            raise
