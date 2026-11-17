
import hashlib
import secrets
import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import RefreshToken

REFRESH_TOKEN_DAYS = 7


def hash_refresh_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_refresh_token(user, family_id=None):
    raw_token = secrets.token_urlsafe(48)

    record = RefreshToken.objects.create(
        user=user,
        token_hash=hash_refresh_token(raw_token),
        family_id=family_id or uuid.uuid4(),
        expires_at=timezone.now()
        + timedelta(days=REFRESH_TOKEN_DAYS),
    )

    return raw_token, record


def rotate_refresh_token(raw_token):
    token_hash = hash_refresh_token(raw_token)
    result = None
    error = None

    with transaction.atomic():
        try:
            record = (
                RefreshToken.objects.select_for_update()
                .select_related("user")
                .get(token_hash=token_hash)
            )
        except RefreshToken.DoesNotExist as exc:
            raise ValueError("Invalid refresh token") from exc

        if record.revoked_at is not None:
            RefreshToken.objects.filter(
                family_id=record.family_id,
                revoked_at__isnull=True,
            ).update(revoked_at=timezone.now())

            error = "Refresh token reuse detected"

        elif record.expires_at <= timezone.now():
            error = "Refresh token expired"

        elif not record.user.is_active:
            error = "User account disabled"

        else:
            new_raw_token, new_record = create_refresh_token(
                record.user,
                family_id=record.family_id,
            )

            record.revoked_at = timezone.now()
            record.replaced_by = new_record
            record.save(
                update_fields=["revoked_at", "replaced_by"]
            )

            result = (new_raw_token, record.user)

    if error:
        raise ValueError(error)

    return result

