
from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from webhooks.models import WebhookEndpoint
from webhooks.serializers import WebhookEndpointSerializer


class WebhookEndpointListCreateView(generics.ListCreateAPIView):
    serializer_class = WebhookEndpointSerializer
    permission_classes = (IsAdminUser,)
    queryset = WebhookEndpoint.objects.all().order_by("-created_at")


class WebhookEndpointDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = WebhookEndpointSerializer
    permission_classes = (IsAdminUser,)
    queryset = WebhookEndpoint.objects.all()
