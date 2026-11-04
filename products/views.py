from rest_framework import viewsets

from .filters import ProductFilter
from .models import Category, Product
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    search_fields = ["name"]


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ["name", "description", "category__name"]
    ordering_fields = ["price", "created_at", "name"]

    def get_queryset(self):
        qs = Product.objects.select_related("category")
        user = self.request.user
        if not (user and user.is_staff):
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer
