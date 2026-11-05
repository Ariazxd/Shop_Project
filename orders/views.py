from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Basket, BasketItem
from .serializers import AddToBasketSerializer, BasketSerializer


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
