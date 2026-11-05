from django.urls import path

from .views import BasketItemAddView, BasketItemDetailView, BasketView

urlpatterns = [
    path("basket/", BasketView.as_view(), name="basket"),
    path("basket/items/", BasketItemAddView.as_view(), name="basket-item-add"),
    path("basket/items/<int:pk>/", BasketItemDetailView.as_view(), name="basket-item-detail"),
]
