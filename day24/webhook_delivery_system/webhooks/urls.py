
from django.urls import path

from webhooks.views import (
    WebhookEndpointDetailView,
    WebhookEndpointListCreateView,
)

urlpatterns = [
    path(
        "endpoints/",
        WebhookEndpointListCreateView.as_view(),
        name="webhook-endpoint-list",
    ),
    path(
        "endpoints/<int:pk>/",
        WebhookEndpointDetailView.as_view(),
        name="webhook-endpoint-detail",
    ),
]
