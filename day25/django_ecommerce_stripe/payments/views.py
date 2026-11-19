
import logging
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.lifecycle import (
    OrderLifecycleError,
    cancel_order_and_restore_stock,
    mark_order_paid,
)
from orders.models import Order

from .services import PaymentError, create_checkout_session

logger = logging.getLogger(__name__)


class CheckoutRequestSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)


class StripeCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            session = create_checkout_session(
                order_id=serializer.validated_data["order_id"],
                user=request.user,
            )

        except PaymentError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except stripe.StripeError:
            logger.exception("Stripe Checkout request failed")

            return Response(
                {"detail": "Stripe is temporarily unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "checkout_session_id": session.id,
                "checkout_url": session.url,
            },
            status=status.HTTP_200_OK,
        )


def verify_checkout_payment(session, order_id):
    """
    Verify that a Stripe Checkout Session matches
    the expected order, amount, and currency.
    """
    try:
        order = Order.objects.get(pk=order_id)

    except (Order.DoesNotExist, ValueError, TypeError):
        return False

    expected_amount = int(
        order.total_amount * Decimal(100)
    )

    return (
        session.get("id") == order.stripe_checkout_session_id
        and session.get("client_reference_id") == str(order.id)
        and session.get("payment_status") == "paid"
        and session.get("currency") == "inr"
        and session.get("amount_total") == expected_amount
    )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Verify Stripe webhook signatures and process
    supported Checkout Session events.
    """

    payload = request.body
    signature = request.headers.get("Stripe-Signature", "")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        return HttpResponse(
            "Webhook not configured.",
            status=503,
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            webhook_secret,
        )

    except (ValueError, stripe.SignatureVerificationError):
        return HttpResponse(
            "Invalid webhook signature.",
            status=400,
        )

    event_type = event["type"]

    supported_events = {
        "checkout.session.completed",
        "checkout.session.async_payment_succeeded",
        "checkout.session.async_payment_failed",
        "checkout.session.expired",
    }

    if event_type not in supported_events:
        return HttpResponse(status=200)

    session = event["data"]["object"]

    # Convert Stripe SDK objects to standard dictionaries.
    if hasattr(session, "to_dict"):
        session = session.to_dict()

    metadata = session.get("metadata") or {}
    order_id = metadata.get("order_id")
    session_id = session.get("id")

    if not order_id or not session_id:
        return HttpResponse(
            "Missing order information.",
            status=400,
        )

    try:
        if event_type == "checkout.session.async_payment_failed":
            # Validate that the event belongs to the stored
            # Checkout Session before acknowledging failure.
            try:
                order = Order.objects.get(pk=order_id)

            except (Order.DoesNotExist, ValueError, TypeError):
                return HttpResponse(
                    "Invalid order.",
                    status=400,
                )

            if order.stripe_checkout_session_id != session_id:
                return HttpResponse(
                    "Checkout session mismatch.",
                    status=409,
                )

            # A failed asynchronous payment does not
            # automatically release reserved inventory.
            # A separate recovery policy will handle it.
            logger.warning(
                "Asynchronous payment failed for Stripe session %s",
                session_id,
            )

            return HttpResponse(status=200)

        elif event_type == "checkout.session.expired":
            # Lifecycle service validates the session ID,
            # prevents duplicate cancellation, and restores
            # reserved inventory exactly once.
            cancel_order_and_restore_stock(
                order_id,
                session_id,
            )

        elif event_type in {
            "checkout.session.completed",
            "checkout.session.async_payment_succeeded",
        }:
            # Checkout completion can precede settlement
            # for asynchronous payment methods.
            if (
                event_type == "checkout.session.completed"
                and session.get("payment_status") != "paid"
            ):
                return HttpResponse(status=200)

            if not verify_checkout_payment(session, order_id):
                logger.warning(
                    "Payment verification failed for session %s",
                    session_id,
                )

                return HttpResponse(
                    "Payment verification failed.",
                    status=400,
                )

            mark_order_paid(
                order_id,
                session_id,
            )

    except OrderLifecycleError:
        logger.warning(
            "Invalid order transition for Stripe session %s",
            session_id,
        )

        return HttpResponse(status=409)

    except Exception:
        logger.exception(
            "Webhook processing failed for session %s",
            session_id,
        )

        return HttpResponse(status=500)

    return HttpResponse(status=200)
