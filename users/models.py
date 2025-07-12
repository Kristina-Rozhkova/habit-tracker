from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(
        verbose_name="Электронная почта",
        help_text="Укажите электронную почту",
        unique=True,
    )
    phone = models.CharField(
        verbose_name="Номер телефона",
        help_text="Укажите номер телефона",
        max_length=35,
        null=True,
        blank=True,
    )
    city = models.CharField(
        verbose_name="Город",
        help_text="Укажите город",
        max_length=50,
        null=True,
        blank=True,
    )
    avatar = models.ImageField(
        upload_to="users/avatars",
        null=True,
        blank=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )
    telegram_chat_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Телеграм ID",
        help_text="Укажите Ваш ID telegram",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
