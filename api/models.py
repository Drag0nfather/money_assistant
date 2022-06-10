from django.db import models

from users.models import CustomUser


class Category(models.Model):
    category_name = models.CharField(
        max_length=30,
    )
    limit = models.IntegerField(
        null=False,
        blank=False,
    )
    fact_spend = models.IntegerField(
        null=True,
        blank=True,
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Пользователь')

    def __str__(self):
        return f'Категория {self.category_name} у пользователя {self.user}'


class SpendItem(models.Model):
    amount = models.IntegerField(
        null=False,
        blank=False
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='Категория')

    def __str__(self):
        return f'Трата {self.amount} р. в категории {self.category}'
