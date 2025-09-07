from rest_framework.serializers import ModelSerializer, SerializerMethodField

from habits.models import Habit
from habits.validators import (
    CheckHabitValidator,
    TimeToCompleteValidator,
    DateDeadlineValidator,
)


class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = "__all__"
        validators = [
            CheckHabitValidator(
                associated_habit="associated_habit",
                reward="reward",
                is_enjoyable="is_enjoyable",
            ),
            TimeToCompleteValidator(time_to_complete="time_to_complete"),
            DateDeadlineValidator(date_deadline="date_deadline"),
        ]
        extra_kwargs = {"owner": {"read_only": True}}
