from django.urls import path

from .views import ProfileView, SignInView, SignOutView, SignUpView

urlpatterns = [
    path("auth/signup/", SignUpView.as_view(), name="signup"),
    path("auth/signin/", SignInView.as_view(), name="signin"),
    path("auth/signout/", SignOutView.as_view(), name="signout"),
    path("profile/", ProfileView.as_view(), name="profile-detail"),
]
