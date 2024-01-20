from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.db import models

from api.v1.validators import validate_username
from api_yamdb.settings import (
    MAX_LENGTH_USERNAME,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_ROLE
)


class User(AbstractUser):
    """Модель пользователя."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    USER_ROLES = [
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    username = models.CharField(
        'Псевдоним',
        max_length=MAX_LENGTH_USERNAME,
        unique=True,
        validators=([UnicodeUsernameValidator(), validate_username])
    )
    email = models.EmailField('Почта', unique=True)
    first_name = models.CharField(
        'Имя', max_length=MAX_LENGTH_FIRST_NAME, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=MAX_LENGTH_LAST_NAME, blank=True
    )
    bio = models.TextField('Личная информация', blank=True)
    role = models.CharField(
        'Права доступа', max_length=MAX_LENGTH_ROLE, choices=USER_ROLES,
        default=USER
    )

    class Meta:
        ordering = ['username']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    def is_moderator(self):
        return self.role == self.MODERATOR

    def __str__(self):
        return self.username
