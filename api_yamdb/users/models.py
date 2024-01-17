from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


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
        max_length=150,
        unique=True,
        validators=([RegexValidator(regex=r'^[\w.@+-]+$')])
    )
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    role = models.CharField(max_length=150, choices=USER_ROLES, default=USER)
    confirmation_code = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        ordering = ['username']
