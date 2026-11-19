
from django.urls import path

from .views import CheckoutView, OrderDetailView, OrderListView

urlpatterns = [
    path("", OrderListView.as_view(), name="order-list"),
    path("checkout/", CheckoutView.as_view(), name="order-checkout"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
