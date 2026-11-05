from rest_framework import serializers

from products.models import Product

from .models import Basket, BasketItem


class BasketItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_price = serializers.IntegerField(source="product.price", read_only=True)
    line_total = serializers.IntegerField(read_only=True)

    class Meta:
        model = BasketItem
        fields = ("id", "product_id", "product_name", "unit_price", "quantity", "line_total")


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Basket
        fields = ("items", "total_items", "total_price")


class AddToBasketSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True), source="product"
    )
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateBasketItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
