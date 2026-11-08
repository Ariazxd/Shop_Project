from django.urls import path

from .views import (
    BasketItemAddView,
    BasketItemDetailView,
    BasketView,
    OrderDetailView,
    OrderListCreateView,
)

from .payment_views import PayOrderView

urlpatterns = [
    path("orders/<int:pk>/pay/", PayOrderView.as_view(), name="order-pay"),
    path("basket/", BasketView.as_view(), name="basket"),
    path("basket/items/", BasketItemAddView.as_view(), name="basket-item-add"),
    path("basket/items/<int:pk>/", BasketItemDetailView.as_view(), name="basket-item-detail"),
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
]
