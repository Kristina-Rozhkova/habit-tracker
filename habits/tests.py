from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch, Mock, MagicMock
from habits import fixtures
from habits.models import Habit
from habits.views import HabitListAPIView, PublicHabitListAPIView, HabitUpdateAPIView, HabitRetrieveAPIView, \
    HabitDestroyAPIView
from users.models import User
from django.test import RequestFactory


class HabitTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="ivanov_ivan@mail.ru", telegram_chat_id="546194525")
        self.user2 = User.objects.create(email="test@mail.ru")
        self.habit = Habit.objects.create(
            action="Выпить стакан воды", owner=self.user
        )
        self.client.force_authenticate(user=self.user)
        self.client.force_authenticate(user=self.user2)
        self.user2.is_superuser = True
        self.user2.save()

        self.factory = RequestFactory()

    @patch('habits.serializers.HabitSerializer.save')
    def test_create(self, mock_save):
        """Проверка создания привычки."""
        data = {
            'action': "Убрать комнату",
            "periodicity": "Ежедневно",
            "owner": self.user
        }

        mock_habit = Habit(**data)
        mock_save.return_value = mock_habit

        request = fixtures.created_habit()

        url = reverse("habits:habit_create")
        response = self.client.post(url, {
            "action": "Убрать комнату",
            "periodicity": "Ежедневно"
        }, format='json')

        mock_save.assert_called_once()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), request)

    @patch('habits.views.Habit.objects.filter')
    def test_list(self, mock_filter):
        """ Проверка получения личных привычек. """
        mock_queryset = [
            Habit(action="Чтение", periodicity="Ежедневно", is_active=False),
            Habit(action="Спорт", periodicity="По понедельникам")
        ]
        mock_filter.return_value = [mock_queryset[1]]

        request = self.factory.get('/habits/my/')
        request.user = self.user

        view = HabitListAPIView()
        view.request = request
        queryset = view.get_queryset()

        mock_filter.assert_called_once_with(owner=self.user, is_active=True)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(queryset[0].action, "Спорт")

    @patch('habits.views.Habit.objects.all')
    def test_list_with_superuser(self, mock_all):
        """ Проверка получения полного списка привычек суперпользователем. """
        mock_queryset = [
            Habit(action="почитать", periodicity="Ежедневно", is_active=False),
            Habit(action="Спорт", periodicity="По понедельникам"),
            Habit(action="Полить цветы", periodicity="Еженедельно", is_public=True),
            Habit(action="Выпить витамины", periodicity="Ежедневно", is_public=False)
        ]
        mock_all.return_value = mock_queryset
        request = self.factory.get('/habits/my/')
        request.user = self.user2

        view = HabitListAPIView()
        view.request = request
        queryset = view.get_queryset()

        mock_all.assert_called_once()
        self.assertEqual(len(queryset), 4)
        self.assertEqual(queryset[0].is_active, False)
        self.assertEqual(str(queryset[0]), 'Сегодня нужно почитать.')

    def test_list_permission_error(self):
        """ Проверка выброса ошибки при попытке получить список собственных привычек неавторизованным пользователем. """
        request = self.factory.get('/habits/my/')
        request.user = AnonymousUser()

        view = HabitListAPIView()
        view.request = request

        with self.assertRaises(PermissionDenied) as ex:
            view.get_queryset()

        self.assertEqual(str(ex.exception), "Требуется авторизация.")

    @patch('habits.views.Habit.objects.filter')
    def test_public_list(self, mock_filter):
        """ Проверка получения публичных привычек. """
        mock_queryset = [
            Habit(action="Полить цветы", periodicity="Еженедельно", is_public=True),
            Habit(action="Выпить витамины", periodicity="Ежедневно", is_public=False)
        ]
        mock_filter.return_value = [mock_queryset[0]]

        request = self.factory.get('/habits/public/')
        request.user = self.user

        view = PublicHabitListAPIView()
        view.request = request

        queryset = view.get_queryset()

        mock_filter.assert_called_once_with(is_public=True)
        self.assertEqual(len(queryset), 1)
        self.assertEqual(str(queryset[0]), "Сегодня нужно Полить цветы.")
        self.assertEqual(queryset[0].is_public, True)

    @patch('habits.serializers.HabitSerializer.save')
    def test_update(self, mock_save):
        """ Проверка успешного редактирования привычки. """
        data = {
            "periodicity": "Ежедневно"
        }

        url = reverse("habits:habit_update", kwargs={'pk': self.habit.pk})

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.habit.periodicity, "Ежедневно")

    def test_update_error(self):
        """ Проверка выброса ошибки при попытке отредактировать чужую привычку. """
        other_user = User.objects.create(email="mihail@mail.ru")
        self.client.force_authenticate(user=other_user)

        request = self.factory.patch(f'/habits/{self.habit.pk}/update/')
        request.user = other_user

        view = HabitUpdateAPIView()
        view.request = request
        view.kwargs = {'pk': self.habit.pk}

        with self.assertRaises(PermissionDenied) as ex:
            view.perform_update(Mock())

        self.assertEqual(str(ex.exception), "У Вас нет прав редактировать эту привычку.")

    @patch('habits.views.HabitRetrieveAPIView.get_object')
    def test_retrieve(self, mock_get_object):
        """ Проверка просмотра детальной информации о непубличной привычке. """
        mock_habit = Habit(action="Выпить витамины", periodicity="Ежедневно", is_public=False, owner=self.user)
        mock_get_object.return_value = mock_habit

        request = self.factory.get(f"/habits/{mock_habit.pk}/detail/")
        request.user = self.user

        view = HabitRetrieveAPIView()
        view.request = request
        view.kwargs = {'pk': mock_habit.pk}

        obj = view.get_object(pk=None)

        mock_get_object.assert_called_once_with(pk=mock_habit.pk)
        self.assertEqual(obj.action, "Выпить витамины")
        self.assertEqual(obj.owner, self.user)

    @patch('habits.views.HabitRetrieveAPIView.get_object')
    def test_retrieve_with_superuser(self, mock_get_object):
        """ Проверка просмотра детальной информации о непубличной привычке суперпользователем. """
        mock_habit = Habit(action="Выпить витамины", periodicity="Ежедневно", is_public=False, owner=self.user)
        mock_get_object.return_value = mock_habit

        request = self.factory.get(f"/habits/{mock_habit.pk}/detail/")
        request.user = self.user2

        view = HabitRetrieveAPIView()
        view.request = request
        view.kwargs = {'pk': mock_habit.pk}

        obj = view.get_object(pk=None)

        mock_get_object.assert_called_once_with(pk=mock_habit.pk)
        self.assertEqual(obj.action, "Выпить витамины")
        self.assertEqual(obj.owner, self.user)

    @patch('habits.views.HabitRetrieveAPIView.get_object')
    def test_public_retrieve(self, mock_get_object):
        """ Проверка просмотра детальной информации о публичной привычке. """
        mock_habit = Habit(action="Выпить витамины", periodicity="Ежедневно", is_public=True, owner=self.user2)
        mock_get_object.return_value = mock_habit

        request = self.factory.get(f"/habits/{mock_habit.pk}/detail/")
        request.user = self.user

        view = HabitRetrieveAPIView()
        view.request = request
        view.kwargs = {'pk': mock_habit.pk}

        obj = view.get_object(pk=None)

        mock_get_object.assert_called_once_with(pk=mock_habit.pk)
        self.assertEqual(obj.action, "Выпить витамины")
        self.assertEqual(obj.owner, self.user2)

    def test_retrieve_error(self):
        """ Проверка выброса ошибки при попытке просмотреть информацию о непубличной привычке. """
        other_user = User.objects.create(email="mihail@mail.ru")
        self.client.force_authenticate(user=other_user)

        request = self.factory.patch(f'/habits/{self.habit.pk}/detail/')
        request.user = other_user

        view = HabitRetrieveAPIView()
        view.request = request
        view.kwargs = {'pk': self.habit.pk}

        with self.assertRaises(PermissionDenied) as ex:
            view.get_object()

        self.assertEqual(str(ex.exception), "У Вас нет прав просматривать информацию об этой привычке.")

    def test_deactivate_habit_by_owner(self):
        """Проверка деактивации привычки создателем. """
        self.user.is_superuser = False
        self.user.save()
        self.client.force_authenticate(user=self.user)

        initial_count = Habit.objects.count()
        habit_pk = self.habit.pk

        self.assertTrue(Habit.objects.get(pk=habit_pk).is_active)

        url = reverse("habits:habit_delete", args=(habit_pk,))
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(Habit.objects.filter(pk=habit_pk).exists(),
                        "Привычка была удалена, а должна быть деактивирована")

        updated_habit = Habit.objects.get(pk=habit_pk)
        self.assertFalse(updated_habit.is_active,
                         f"Привычка не деактивирована. Текущее состояние: {updated_habit.is_active}")
        self.assertEqual(Habit.objects.count(), initial_count,
                         f"Количество привычек изменилось с {initial_count} на {Habit.objects.count()}")

    @patch('habits.views.Habit.objects.get')
    def test_delete(self, mock_get):
        """ Проверка успешного удаления привычки суперпользователем. """
        mock_habit = MagicMock()
        mock_get.return_value = mock_habit

        request = self.factory.delete(f'/habits/{self.habit.pk}/delete/')
        request.user = self.user2

        view = HabitDestroyAPIView()
        view.request = request
        view.kwargs = {'pk': self.habit.pk}
        response = view.destroy(request)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_error(self):
        """ Проверка выброса ошибки при попытке удалить чужую привычку. """
        other_user = User.objects.create(email="mihail@mail.ru")
        self.client.force_authenticate(user=other_user)

        request = self.factory.delete(f'/habits/{self.habit.pk}/delete/')
        request.user = other_user

        view = HabitDestroyAPIView()
        view.request = request
        view.kwargs = {'pk': self.habit.pk}

        with self.assertRaises(PermissionDenied) as ex:
            view.destroy(request)

        self.assertEqual(str(ex.exception), "У вас нет прав на удаление этой привычки.")
