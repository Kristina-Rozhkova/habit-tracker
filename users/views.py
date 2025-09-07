from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny
from .models import User
from .serializers import UserDetailSerializer, UserSerializer, UserCreateSerializer


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="Создание пользователя",
        operation_description="Создание нового пользователя. Для авторизации требуются email и пароль.",
    ),
)
class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Список пользователей",
        operation_description="Вывод списка авторизованных пользователей. Требуется авторизация. Для просмотра доступны "
        "поля: email, имя, город, аватар.",
        responses={200: UserSerializer(many=True)},
    ),
)
class UserListAPIView(ListAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        user = self.request.user

        if user.is_superuser:
            return UserSerializer
        raise PermissionDenied


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="Просмотр профиля",
        operation_description="Просмотр профиля пользователя. Требуется авторизация. Для владельца профиля и администратора"
        " для просмотра доступны поля: email, имя, фамилия, телефон, город, аватар, история платежей."
        " Для других пользователей на просмотр доступны поля: email, имя, город, аватар.",
        responses={
            200: openapi.Response(
                description="Успешный ответ",
                examples={
                    "application/json": {
                        "Для владельца/админа": UserDetailSerializer().data,
                        "Для других": {
                            "email": "",
                            "first_name": "",
                            "city": "",
                            "avatar": "",
                        },
                    }
                },
            )
        },
    ),
)
class UserRetrieveAPIView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

    def get_serializer_class(self):
        user = self.request.user
        requested_user = self.get_object()

        if user.is_staff or user.is_superuser or user.id == requested_user.id:
            return UserDetailSerializer
        raise PermissionDenied("Нет прав для просмотра информации о пользователе.")


@method_decorator(
    name="put",
    decorator=swagger_auto_schema(
        operation_summary="Редактирование профиля",
        operation_description="Редактирование полей профиля пользователя. Требуется авторизация. Для владельца профиля и "
        "администратора для редактирования доступны поля: email, имя, фамилия, телефон, город, "
        "аватар, история платежей.",
        responses={200: UserDetailSerializer(many=True)},
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="Частичное редактирование профиля",
        operation_description="Обновление отдельных полей профиля пользователя. Требуется авторизация. Для владельца "
        "профиля и администратора для обновления доступны поля: email, имя, фамилия, телефон, город, "
        "аватар, история платежей.",
        responses={200: UserDetailSerializer(many=True)},
    ),
)
class UserUpdateAPIView(UpdateAPIView):
    queryset = User.objects.all()

    def get_serializer_class(self):
        user = self.request.user
        requested_user = self.get_object()

        if user.is_staff or user.is_superuser or user.id == requested_user.id:
            return UserDetailSerializer
        raise PermissionDenied("Нет прав для редактирования информации.")


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="Удаление пользователя",
        operation_description="Удаление пользователя из базы данных. Доступно только для владельца профиля.",
    ),
)
class UserDestroyAPIView(DestroyAPIView):
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(pk=user.pk)
