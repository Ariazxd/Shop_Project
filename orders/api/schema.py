"""Response shapes and query parameters shown in Swagger (docs only)."""
from drf_yasg import openapi
from rest_framework import serializers


class DetailSerializer(serializers.Serializer):
    detail = serializers.CharField()


class PayOrderResponseSerializer(serializers.Serializer):
    authority = serializers.CharField()
    payment_url = serializers.URLField()


class VerifyPaymentResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
    order_id = serializers.IntegerField()
    ref_id = serializers.CharField(required=False)


VERIFY_PARAMETERS = [
    openapi.Parameter(
        "Authority", openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description="Authority returned by /pay/",
    ),
    openapi.Parameter(
        "Status", openapi.IN_QUERY, type=openapi.TYPE_STRING,
        description="OK or NOK (sent by Zarinpal)",
    ),
]
