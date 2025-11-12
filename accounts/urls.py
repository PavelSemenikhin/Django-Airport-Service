from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from accounts.views import (
    CreateUserViewSet,
    ProfileViewSet,
)


app_name = "accounts"

urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path(
        "register/",
        CreateUserViewSet.as_view({"post": "create"}),
        name="register"
    ),
    path(
        "me/",
        ProfileViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "put": "update"}
        ),
        name="me",
    ),
]
