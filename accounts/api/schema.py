"""Response shapes shown in Swagger (they do not change the real responses)."""
from rest_framework import serializers

from .serializers import SignUpSerializer


class SignUpResponseSerializer(serializers.Serializer):
    user = SignUpSerializer()
    token = serializers.CharField()


class SignInResponseSerializer(serializers.Serializer):
    token = serializers.CharField()
    username = serializers.CharField()
