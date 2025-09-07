from celery import shared_task

from habits.models import Habit
from habits.services import send_telegram_message
from users.models import User


@shared_task
def send_reminder_with_bot(habit_id):
    """ Отправка напоминания о привычке с помощью телеграм-бота. """
    habit = Habit.objects.get(id=habit_id)

    send_telegram_message(str(habit), habit.owner.telegram_chat_id)
