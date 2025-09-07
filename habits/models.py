from django.db import models
from users.models import User


class Habit(models.Model):
    EVERY_DAY = "Ежедневно"
    EVERY_WEEK = "Еженедельно"
    EVERY_TWO_DAYS = "Каждые 2 дня"
    EVERY_THREE_DAYS = "Каждые 3 дня"
    EVERY_FOUR_DAYS = "Каждые 4 дня"
    MONDAY = "По понедельникам"
    TUESDAY = "По вторникам"
    WEDNESDAY = "По средам"
    THURSDAY = "По четвергам"
    FRIDAY = "По пятницам"
    SATURDAY = "По субботам"
    SUNDAY = "По воскресеньям"
    TWO_TIMES_IN_DAY = "2 раза в день"
    THREE_TIMES_IN_DAY = "3 раза в день"

    PERIODICITY_IN_CHOICES = [
        (EVERY_WEEK, "Еженедельно"),
        (EVERY_DAY, "Ежедневно"),
        (EVERY_TWO_DAYS, "Каждые 2 дня"),
        (EVERY_THREE_DAYS, "Каждые 3 дня"),
        (EVERY_FOUR_DAYS, "Каждые 4 дня"),
        (MONDAY, "По понедельникам"),
        (TUESDAY, "По вторникам"),
        (WEDNESDAY, "По четвергам"),
        (THURSDAY, "По четвергам"),
        (FRIDAY, "По пятницам"),
        (SATURDAY, "По субботам"),
        (SUNDAY, "По воскресеньям"),
        (TWO_TIMES_IN_DAY, "2 раза в день"),
        (THREE_TIMES_IN_DAY, "3 раза в день"),
    ]

    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, verbose_name="Автор", null=True, blank=True
    )
    place = models.CharField(
        max_length=30,
        verbose_name="Место",
        help_text="Место, в котором необходимо выполнять привычку",
        null=True,
        blank=True,
    )
    date_deadline = models.DateField(
        verbose_name="Дата выполнения привычки",
        help_text="Дата, когда необходимо выполнять привычку",
        null=True,
        blank=True,
    )
    time_deadline = models.TimeField(
        verbose_name="Время выполнения привычки",
        help_text="Время, когда необходимо выполнять привычку",
        null=True,
        blank=True,
    )
    action = models.CharField(
        max_length=50,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка",
    )
    is_enjoyable = models.BooleanField(
        verbose_name="Признак приятной привычки",
        help_text="Привычка, способ вознаградить себя за выполнение полезной привычки",
        null=True,
        blank=True,
    )
    associated_habit = models.ForeignKey(
        "Habit",
        on_delete=models.CASCADE,
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой, важно указывать для полезных привычек, но не для "
        "приятных",
        null=True,
        blank=True,
    )
    periodicity = models.CharField(
        max_length=16,
        choices=PERIODICITY_IN_CHOICES,
        default=EVERY_DAY,
        verbose_name="Периодичность",
        help_text="Периодичность выполнения привычки для напоминания в днях",
    )
    reward = models.CharField(
        max_length=50,
        verbose_name="Вознаграждение",
        help_text="Вознаграждение за выполнение привычки",
        null=True,
        blank=True,
    )
    time_to_complete = models.PositiveIntegerField(
        verbose_name="Время на выполнение",
        help_text="Время, которое предположительно нужно потратить на выполнение привычки. Укажите в минутах",
        null=True,
        blank=True,
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Привычки можно публиковать в общий доступ, чтобы другие пользователи могли брать в пример Ваши "
        "привычки",
    )
    is_active = models.BooleanField(verbose_name="Признак активности", default=True)

    def __str__(self):
        return f"Сегодня нужно {self.action}."

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
