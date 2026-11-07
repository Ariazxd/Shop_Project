from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Basket, BasketItem, Order
from .serializers import (
    AddToBasketSerializer,
    BasketSerializer,
    OrderSerializer,
    UpdateBasketItemSerializer,
)


def get_basket(user):
    basket, _ = Basket.objects.get_or_create(user=user)
    return basket


class BasketView(APIView):
    """GET: show basket. DELETE: empty basket."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(BasketSerializer(get_basket(request.user)).data)

    def delete(self, request):
        get_basket(request.user).items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BasketItemAddView(APIView):
    """POST {product_id, quantity}: add a product (quantity is summed if it already exists)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToBasketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        basket = get_basket(request.user)
        item = BasketItem.objects.filter(basket=basket, product=product).first()
        new_quantity = quantity + (item.quantity if item else 0)
        if new_quantity > product.stock:
            return Response(
                {"detail": f"Only {product.stock} unit(s) of '{product.name}' in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if item:
            item.quantity = new_quantity
            item.save()
        else:
            BasketItem.objects.create(basket=basket, product=product, quantity=quantity)
        return Response(BasketSerializer(basket).data, status=status.HTTP_201_CREATED)


class BasketItemDetailView(APIView):
    """PATCH {quantity}: change quantity. DELETE: remove item."""

    permission_classes = [permissions.IsAuthenticated]

    def get_item(self, request, pk):
        return get_object_or_404(
            BasketItem.objects.select_related("product"),
            pk=pk,
            basket__user=request.user,
        )

    def patch(self, request, pk):
        item = self.get_item(request, pk)
        serializer = UpdateBasketItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data["quantity"]
        if quantity > item.product.stock:
            return Response(
                {"detail": f"Only {item.product.stock} unit(s) in stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.quantity = quantity
        item.save()
        return Response(BasketSerializer(item.basket).data)

    def delete(self, request, pk):
        item = self.get_item(request, pk)
        basket = item.basket
        item.delete()
        return Response(BasketSerializer(basket).data)


class OrderListCreateView(generics.ListAPIView):
    """GET /api/orders/ -> my orders."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
