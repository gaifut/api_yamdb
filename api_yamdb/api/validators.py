from django.utils import timezone
from rest_framework import serializers

VALIDATE_DATE_ERROR = 'Год выпуска не может быть больше {year}'


def validate_date(value):
    year = timezone.datetime.now().year
    if value > timezone.datetime.now().year:
        raise serializers.ValidationError(
            VALIDATE_DATE_ERROR.format(year=year)
        )


def validate_username(value):
    """Валидация поля юзернейма в сериализаторах и модели."""
    if value == 'me':
        raise serializers.ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )
    return value
