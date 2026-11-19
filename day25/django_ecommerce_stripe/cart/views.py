from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    UpdateCartItemSerializer,
)


def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_user_cart(request.user)
        items = cart.items.select_related("product")
        serializer = CartItemSerializer(items, many=True)

        total = sum(
            (item.subtotal for item in items),
            start=Decimal("0.00"),
        )

        return Response({
            "cart_id": cart.id,
            "items": serializer.data,
            "total": str(total),
        })


class CartItemCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]
        cart = get_user_cart(request.user)

        with transaction.atomic():
            item, created = CartItem.objects.select_for_update().get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity},
            )

            if not created:
                item.quantity += quantity
                item.save(update_fields=["quantity"])

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CartItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_item(self, request, pk):
        return get_object_or_404(
            CartItem,
            pk=pk,
            cart__user=request.user,
        )

    def patch(self, request, pk):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            item = get_object_or_404(
                CartItem.objects.select_for_update(),
                pk=pk,
                cart__user=request.user,
            )
            item.quantity = serializer.validated_data["quantity"]
            item.save(update_fields=["quantity"])

        return Response(CartItemSerializer(item).data)

    def delete(self, request, pk):
        item = self.get_item(request, pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)