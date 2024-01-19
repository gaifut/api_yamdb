from django.core.validators import (
    MaxValueValidator, MinValueValidator, RegexValidator
)
from django.db import models

from api.validators import validate_date
from users.models import User


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
        ordering = ['name']

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
        ordering = ['name']

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


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(
                1, message='Минимайльный рейтинг - 1.'
            ),
            MaxValueValidator(
                10, message='Максимальный рейтинг - 10'
            ),
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'], name='unique_author_title'
            )]
        ordering = ['-pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.name
