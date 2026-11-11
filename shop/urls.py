from django.contrib import admin
from django.urls import include, path, re_path

from .schema import schema_view

urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
    path("api/v1/", include("accounts.api.urls")),
    path("api/v1/", include("products.api.urls")),
    path("api/v1/", include("orders.api.urls")),
]
