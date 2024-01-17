from django.core.validators import RegexValidator
from django.db import models

from api.validators import validate_date


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Имя категории')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг',
        validators=[RegexValidator(regex=r'^[a-zA-Z]+$')]
    )

    class Meta:
        verbose_name = 'Категория'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Имя жанра')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг',
        validators=[RegexValidator(regex=r'^[a-zA-Z]+$')]
    )

    class Meta:
        verbose_name = 'Жанр'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Имя жанра')
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Слаг')

    class Meta:
        verbose_name = 'Жанр'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name=('Название произведения'),
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        through='GenreTitle',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True,
        verbose_name='Категория',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    year = models.IntegerField(
        db_index=True,
        validators=[validate_date],
        verbose_name='Год выпуска'
    )

    class Meta:
        verbose_name = 'Произведение'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='genretitle',
    )
    genre = models.ForeignKey(
        Genre,
        related_name='genretitle',
        on_delete=models.SET_NULL,
        verbose_name='Жанр',
        blank=True,
        null=True,
    )
