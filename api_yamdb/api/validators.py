from django.utils import timezone
from rest_framework import serializers

VALIDATE_DATE_ERROR = 'Год выпуска не может быть больше {year}'


def validate_date(value):
    if value > timezone.datetime.now().year:
        raise serializers.ValidationError(
            VALIDATE_DATE_ERROR.format(year=timezone.datetime.now().year)
        )
