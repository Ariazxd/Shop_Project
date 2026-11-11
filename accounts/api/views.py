from django.utils.decorators import method_decorator
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ProfileSerializer,
    SignInResponseSerializer,
    SignInSerializer,
    SignUpResponseSerializer,
    SignUpSerializer,
)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(responses={201: SignUpResponseSerializer}),
)
class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"user": serializer.data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


class SignInView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=SignInSerializer, responses={200: SignInResponseSerializer}
    )
    def post(self, request):
        serializer = SignInSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})


class SignOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=no_body, responses={204: "Token deleted"})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(responses={204: "Account deleted"}),
)
class ProfileView(generics.RetrieveUpdateDestroyAPIView):
    """
    Detail / update / delete for the *current* user's profile.
    There is intentionally no list endpoint.
    Create happens automatically on sign up (post_save signal).
    """

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def destroy(self, request, *args, **kwargs):
        # Deleting the profile deletes the account (profile cascades with the user).
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
