
import uuid

from django.conf import settings
from django.db import models


class RefreshToken(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refresh_tokens",
    )

    token_hash = models.CharField(
        max_length=64,
        unique=True,
    )

    family_id = models.UUIDField(default=uuid.uuid4)

    expires_at = models.DateTimeField()

    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    replaced_by = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refresh token {self.id}"
