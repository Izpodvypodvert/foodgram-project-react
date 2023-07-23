import csv

from django.conf import settings
from django.core.management import BaseCommand
from django.db import IntegrityError


from foodgram.models import (
    Ingredient,
    Tag,
)

TABLES = {
    Ingredient: 'ingredients.csv',
    Tag: 'tags.csv',
}


class Command(BaseCommand):
    """Загрузка данных из папки static/data."""

    def handle(self, *args, **kwargs):
        for model, csv_f in TABLES.items():
            with open(
                    f'{settings.BASE_DIR}/foodgram/data/{csv_f}',
                    'r',
                    encoding='utf-8'
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                try:
                    model.objects.bulk_create(
                        model(**data) for data in reader)
                except IntegrityError:
                    self.stdout.write(self.style.ERROR_OUTPUT(
                        'данные уже были загружены! Или ошибки в csv файлах!'))
                    continue
        self.stdout.write(self.style.SUCCESS('Все данные загружены'))
