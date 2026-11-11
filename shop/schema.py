"""Swagger / ReDoc setup (drf-yasg). The URLs are wired in shop/urls.py."""
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Shop API",
        default_version="v1",
        description=(
            "Shop backend: accounts, products, favorites, basket, orders and "
            "Zarinpal (sandbox) payment."
        ),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
