from django.urls import path

from .views import SignInView, SignOutView, SignUpView

urlpatterns = [
    path("auth/signup/", SignUpView.as_view(), name="signup"),
    path("auth/signin/", SignInView.as_view(), name="signin"),
    path("auth/signout/", SignOutView.as_view(), name="signout"),
]
