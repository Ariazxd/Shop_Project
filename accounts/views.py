from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, permissions, serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProfileSerializer, SignInSerializer, SignUpSerializer


SignUpResponse = inline_serializer(
    "SignUpResponse",
    {"user": SignUpSerializer(), "token": serializers.CharField()},
)
SignInResponse = inline_serializer(
    "SignInResponse",
    {"token": serializers.CharField(), "username": serializers.CharField()},
)


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={201: SignUpResponse})
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

    @extend_schema(request=SignInSerializer, responses={200: SignInResponse})
    def post(self, request):
        serializer = SignInSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username})


class SignOutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

    @extend_schema(responses={204: None})
    def destroy(self, request, *args, **kwargs):
        # Deleting the profile deletes the account (profile cascades with the user).
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
