
import time

import pyotp
from django.db import transaction

from accounts.models import TOTPDevice


def generate_totp_secret():
    return pyotp.random_base32()


def generate_totp_uri(secret, username):
    return pyotp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name="Day23AuthLab",
    )


def verify_totp(secret, code):
    if not secret or not code:
        return False

    return pyotp.TOTP(secret).verify(
        str(code),
        valid_window=0,
    )
def verify_totp_once(user, code):
    with transaction.atomic():
        try:
            device = TOTPDevice.objects.select_for_update().get(
                user=user
            )
        except TOTPDevice.DoesNotExist:
            return False

        if not device.is_verified:
            return False

        current_step = int(time.time()) // 30

        if (
            device.last_used_step is not None
            and current_step <= device.last_used_step
        ):
            return False

        if not pyotp.TOTP(device.secret).verify(
            str(code),
            valid_window=0,
        ):
            return False

        device.last_used_step = current_step
        device.save(update_fields=["last_used_step"])

        return True
