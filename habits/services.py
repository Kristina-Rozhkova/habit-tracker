from datetime import datetime, timedelta

from django_celery_beat.models import IntervalSchedule, PeriodicTask, CrontabSchedule
import json
from config.settings import TELEGRAM_URL, TELEGRAM_BOT_TOKEN
import requests
from habits.models import Habit


def need_to_send(periodicity):
    """ Проверка, в какой день недели нужно отправлять уведомление. """

    if periodicity == Habit.MONDAY:
        return '1'
    elif periodicity == Habit.TUESDAY:
        return '2'
    elif periodicity == Habit.WEDNESDAY:
        return '3'
    elif periodicity == Habit.THURSDAY:
        return '4'
    elif periodicity == Habit.FRIDAY:
        return '5'
    elif periodicity == Habit.SATURDAY:
        return '6'
    else:
        return '0'


def send_telegram_message(message, chat_id):
    params = {
        "text": message,
        "chat_id": chat_id
    }
    requests.get(f'{TELEGRAM_URL}{TELEGRAM_BOT_TOKEN}/sendMessage', params=params)


def set_schedule_every_day(habit_id, periodicity):

    if periodicity == 'Ежедневно':
        every = 1

    elif periodicity == 'Еженедельно':
        every = 7

    elif periodicity == 'Каждые 2 дня':
        every = 2

    elif periodicity == 'Каждые 3 дня':
        every = 3

    elif periodicity == 'Каждые 4 дня':
        every = 4

    schedule, created = IntervalSchedule.objects.get_or_create(
        every=every,
        period=IntervalSchedule.DAYS,
    )

    PeriodicTask.objects.create(
        interval=schedule,
        name='Habit Reminder Bot',
        task='habits.tasks.send_reminder_with_bot',
        args=json.dumps([habit_id]),
        kwargs=json.dumps({}),
        expires=datetime.utcnow() + timedelta(days=1)
    )


def set_schedule_a_few_time(habit_id, periodicity):

    if periodicity == '2 раза в день':
        hours = '9,17'

    elif periodicity == '3 раза в день':
        hours = '8,14,19'

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour=hours,
        day_of_month='*',
        month_of_year='*',
        day_of_week='*',
        timezone='Europe/Moscow'
    )

    PeriodicTask.objects.update_or_create(
        name=f'habit_{habit_id}_crontab',
        crontab=schedule,
        task='habits.tasks.send_reminder_with_bot',
        args=json.dumps([habit_id]),
        enabled=True,
        one_off=False
    )


def set_schedule_every_weekday(habit_id, periodicity):
    day_of_week = need_to_send(periodicity)

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='8',
        day_of_month='*',
        month_of_year='*',
        day_of_week=day_of_week,
        timezone='Europe/Moscow'
    )

    PeriodicTask.objects.update_or_create(
        name=f'habit_{habit_id}_crontab',
        crontab=schedule,
        task='habits.tasks.send_reminder_with_bot',
        args=json.dumps([habit_id]),
        enabled=True,
        one_off=False
    )
