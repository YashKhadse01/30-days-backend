
from django.conf import settings
from django.db import models


class TOTPDevice(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="totp_device",
    )

    secret = models.CharField(max_length=64)

    is_verified = models.BooleanField(default=False)

    last_used_step = models.BigIntegerField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TOTP device for {self.user_id}"
