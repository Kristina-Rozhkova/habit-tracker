from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class UserTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(email="admin@mail.ru")
        self.client.force_authenticate(user=self.user)

    def test_user_create(self):
        """Тестирование создания пользователя."""
        data = {"email": "stanislav@list.ru", "password": "111111"}

        url = reverse("users:user-create")
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(User.objects.all().count(), 2)

    def test_user_token(self):
        """Тестирование получения токена для пользователя."""
        self.user.set_password("123")
        self.user.save()
        data = {"email": self.user.email, "password": "123"}

        token_url = reverse("users:token_obtain_pair")
        response = self.client.post(token_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_token_refresh(self):
        """Тестирование обновления токена для пользователя."""
        self.user.set_password("123")
        self.user.save()
        data = {"email": self.user.email, "password": "123"}

        token_url = reverse("users:token_obtain_pair")
        token_response = self.client.post(token_url, data)
        refresh_token = token_response.json()["refresh"]

        refresh_data = {"refresh": refresh_token}

        refresh_token_url = reverse("users:token_refresh")
        response = self.client.post(refresh_token_url, refresh_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list(self):
        """Тестирование просмотра списка пользователей."""
        url = reverse("users:user-list")

        # Тест для суперпользователя
        self.user.is_superuser = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()[0]
        self.assertEqual(response_data["email"], self.user.email)
        self.assertEqual(response_data["first_name"], "")

        # Тест для обычного пользователя
        regular_user = User.objects.create(email="regular@mail.ru")
        self.client.force_authenticate(user=regular_user)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail(self):
        """Тестирование просмотра профиля пользователя."""
        url = reverse("users:user-detail", args=(self.user.pk,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertEqual(response_data["email"], self.user.email)

    def test_another_user_detail(self):
        """Тестирование просмотра профиля пользователя другим пользователем."""
        other_user = User.objects.create(email="other@mail.ru", password="testpass123")
        self.client.force_authenticate(user=other_user)

        url = reverse("users:user-detail", args=[self.user.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['detail'],
            "Нет прав для просмотра информации о пользователе."
        )

    def test_user_update(self):
        """Тестирование обновления профиля"""
        data = {"city": "Москва"}

        url = reverse("users:user-update", args=(self.user.pk,))
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.json(),
            {
                'id': self.user.pk,
                'email': 'admin@mail.ru',
                'first_name': '',
                'last_name': '',
                'phone': None,
                'city': 'Москва',
                'avatar': None,
                'telegram_chat_id': None
            },
        )

    def test_user_delete_with_superuser(self):
        """Тестирование удаления пользователя суперпользователем."""
        self.superuser = User.objects.create(
            email="superuser@mail.ru",
            is_superuser=True
        )
        self.client.force_authenticate(user=self.superuser)
        url = reverse("users:user-delete", args=[self.user.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_user_delete(self):
        """ Тестирование удаления пользователем самого себя. """
        url = reverse("users:user-delete", args=[self.user.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_error(self):
        """ Тестирование удаления пользователем другого пользователя. """
        other_user = User.objects.create(email="other@mail.ru")
        self.client.force_authenticate(user=self.user)

        url = reverse("users:user-delete", args=[other_user.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
