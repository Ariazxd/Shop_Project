from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import ProfileView, SignInView, SignOutView, SignUpView

urlpatterns = [
    path("auth/signup/", SignUpView.as_view(), name="signup"),
    path("auth/signin/", SignInView.as_view(), name="signin"),
    path("auth/signout/", SignOutView.as_view(), name="signout"),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile-detail"),
]
