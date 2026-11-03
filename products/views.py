from rest_framework import mixins, viewsets

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None


class ProductViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    def get_queryset(self):
        return Product.objects.select_related("category").filter(is_active=True)

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
