from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Basket
from .serializers import BasketSerializer


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
