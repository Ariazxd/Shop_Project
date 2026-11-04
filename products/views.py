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
    """
    list     GET    /api/products/            (search + filter + ordering)
    retrieve GET    /api/products/<id>/       (product detail)
    create   POST   /api/products/            (staff only)
    update   PUT/PATCH /api/products/<id>/    (staff only)
    destroy  DELETE /api/products/<id>/       (staff only)

    Query params: ?search=  ?category=  ?category_slug=  ?min_price=  ?max_price=
                  ?in_stock=true|false  ?ordering=price|-price|created_at|-created_at
    """

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
