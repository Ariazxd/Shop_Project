"""Response shapes shown in Swagger (they do not change the real responses)."""
from rest_framework import serializers


class FavoriteResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
