from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    FavoriteListView,
    ProductFavoriteView,
    ProductViewSet,
)

router = DefaultRouter()
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path(
        "products/<int:pk>/favorite/",
        ProductFavoriteView.as_view(),
        name="product-favorite",
    ),
    path("favorites/", FavoriteListView.as_view(), name="favorite-list"),
    path("", include(router.urls)),
]
