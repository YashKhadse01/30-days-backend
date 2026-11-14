
import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from orm_lab.models import Review

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Review)
def review_saved(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "New review created: Book=%s, Rating=%s",
            instance.book_id,
            instance.rating,
        )
    else:
        logger.info(
            "Review updated: ID=%s",
            instance.pk,
        )


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance, **kwargs):
    logger.info(
        "Review deleted: ID=%s",
        instance.pk,
    )
