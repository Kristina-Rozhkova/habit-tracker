from django.urls import path
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig

from .views import (
    UserCreateAPIView,
    UserDestroyAPIView,
    UserListAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView,
)

app_name = UsersConfig.name


TokenObtainPairView = method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Получение JWT-токенов",
        operation_description="После авторизации доступна функция получение токена. При запросе необходимо указать "
        "email, пароль. При успешной обработке запроса выводится access токен и refresh токен.",
    ),
)(TokenObtainPairView)

TokenRefreshView = method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Обновление access токена",
        operation_description="Возможность обновления access токена. Для этого необходимо в запрос передать refresh "
        "токен.",
    ),
)(TokenRefreshView)

urlpatterns = [
    path("", UserListAPIView.as_view(), name="user-list"),
    path("create/", UserCreateAPIView.as_view(), name="user-create"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-detail"),
    path("<int:pk>/update/", UserUpdateAPIView.as_view(), name="user-update"),
    path("<int:pk>/delete/", UserDestroyAPIView.as_view(), name="user-delete"),
    path(
        "token/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
]
