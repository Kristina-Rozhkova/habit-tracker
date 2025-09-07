from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueValidator
from .models import User
from rest_framework import serializers


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class UserCreateSerializer(ModelSerializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Пользователь с таким email уже зарегистрирован.")
        ]
    )
    class Meta:
        model = User
        fields = "__all__"


class UserDetailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "telegram_chat_id",
        ]
