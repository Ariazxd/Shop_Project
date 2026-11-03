from rest_framework import serializers

from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "category", "price", "in_stock")
