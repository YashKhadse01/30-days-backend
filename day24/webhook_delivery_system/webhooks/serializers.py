
from typing import ClassVar
from urllib.parse import urlsplit

from rest_framework import serializers

from webhooks.models import WebhookEndpoint


class WebhookEndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEndpoint

        fields = (
            "id",
            "url",
            "secret",
            "is_active",
            "created_at",
        )

        read_only_fields = ("id", "created_at")

        extra_kwargs: ClassVar[dict] = {
            "secret": {
                "write_only": True,
                "required": True,
                "min_length": 16,
                "trim_whitespace": False,
            },
        }

    def validate_url(self, value):
        parsed = urlsplit(value)

        is_local_http = (
            parsed.scheme == "http"
            and parsed.hostname in {"127.0.0.1", "localhost"}
        )

        if parsed.scheme != "https" and not is_local_http:
            raise serializers.ValidationError(
                "HTTPS is required except for local development."
            )

        return value
