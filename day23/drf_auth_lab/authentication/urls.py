
from django.urls import path

from .login_views import LoginView
from .refresh_views import RefreshTokenView
from .views import ProfileView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshTokenView.as_view(), name="refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
