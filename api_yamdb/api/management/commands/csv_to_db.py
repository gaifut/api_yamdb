import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from api.models import (Category, Genre, GenreTitle, Title)


def category_create(row):
    Category.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def genre_create(row):
    Genre.objects.get_or_create(
        id=row[0],
        name=row[1],
        slug=row[2],
    )


def titles_create(row):
    Title.objects.get_or_create(
        id=row[0],
        name=row[1],
        year=row[2],
        category_id=row[3],
    )


def genre_title_create(row):
    GenreTitle.objects.get_or_create(
        id=row[0],
        genre_id=row[2],
        title_id=row[1],
    )


FILES = {
    'category.csv': category_create,
    'genre.csv': genre_create,
    'titles.csv': titles_create,
    'genre_title.csv': genre_title_create,
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'static/data/')
        for key in FILES.keys():
            with open(path + key, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    FILES[key](row)
