from rest_framework import mixins, viewsets

from .models import Product
from .serializers import ProductListSerializer


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return Product.objects.select_related("category").filter(is_active=True)
