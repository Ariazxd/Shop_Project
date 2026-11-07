from django.urls import path

from .views import (
    BasketItemAddView,
    BasketItemDetailView,
    BasketView,
    OrderDetailView,
    OrderListCreateView,
)

urlpatterns = [
    path("basket/", BasketView.as_view(), name="basket"),
    path("basket/items/", BasketItemAddView.as_view(), name="basket-item-add"),
    path("basket/items/<int:pk>/", BasketItemDetailView.as_view(), name="basket-item-detail"),
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
