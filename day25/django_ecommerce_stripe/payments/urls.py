from django.urls import path

from .views import StripeCheckoutView, stripe_webhook

urlpatterns = [
    path(
        "checkout/",
        StripeCheckoutView.as_view(),
        name="stripe-checkout",
    ),
    path(
        "webhook/",
        stripe_webhook,
        name="stripe-webhook",
    ),
]