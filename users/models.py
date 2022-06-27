from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Meta:
        ordering = ['-id']

    username = models.CharField(
        max_length=30,
        unique=True,
        blank=False,
        null=False
    )
    name = models.CharField(max_length=30, null=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
        blank=False,
        null=False
    )
    money = models.IntegerField(
        null=True,
    )
    payment_date = models.DateField(
        null=True,
    )
    day_balance = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True
    )
    period_begin_money = models.DecimalField(
        decimal_places=2,
        max_digits=10,
        null=True
    )

    def __str__(self):
        return self.username
