from django.shortcuts import get_object_or_404
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import generics, permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import ProductFilter
from ..models import Category, Favorite, Product
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
    list     GET    /api/v1/products/            (search + filter + ordering)
    retrieve GET    /api/v1/products/<id>/       (product detail)
    create   POST   /api/v1/products/            (staff only)
    update   PUT/PATCH /api/v1/products/<id>/    (staff only)
    destroy  DELETE /api/v1/products/<id>/       (staff only)

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


class FavoriteResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class ProductFavoriteView(APIView):
    """
    POST   /api/v1/products/<id>/favorite/  -> add to my favorites (201, or 200 if already there)
    DELETE /api/v1/products/<id>/favorite/  -> remove from my favorites (204, also if it was not there)
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=no_body,
        responses={201: FavoriteResponseSerializer, 200: FavoriteResponseSerializer},
    )
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, is_active=True)
        _, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if created:
            return Response(
                {"detail": "Added to favorites."}, status=status.HTTP_201_CREATED
            )
        return Response({"detail": "Already in favorites."})

    @swagger_auto_schema(responses={204: "Removed"})
    def delete(self, request, pk):
        Favorite.objects.filter(user=request.user, product_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteListView(generics.ListAPIView):
    """GET /api/v1/favorites/ -> my favorite products, most recently added first."""

    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # schema generation, no user
            return Product.objects.none()
        # Filter and order go through the same favorite row (the join is reused).
        return (
            Product.objects.filter(favorited_by__user=self.request.user, is_active=True)
            .select_related("category")
            .order_by("-favorited_by__created_at", "-favorited_by__id")
        )
