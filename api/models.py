from django.db import models

from users.models import CustomUser


class Category(models.Model):
    category_name = models.CharField(
        max_length=30,
        unique=True,
    )
    limit = models.IntegerField(
        null=False,
        blank=False,
    )

    def __str__(self):
        return self.category_name


class UserCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='Категория')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Пользователь')

    def __str__(self):
        return f'Категория {self.category} у пользователя {self.user}'


class SpendItem(models.Model):
    amount = models.IntegerField(
        null=False,
        blank=False
    )
    category = models.ForeignKey(UserCategory, on_delete=models.CASCADE, related_name='Категория')

    def __str__(self):
        return f'Трата {self.amount} р. в категории {self.category}'
