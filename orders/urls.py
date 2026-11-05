from django.urls import path

from .views import BasketItemAddView, BasketView

urlpatterns = [
    path("basket/", BasketView.as_view(), name="basket"),
    path("basket/items/", BasketItemAddView.as_view(), name="basket-item-add"),
]
