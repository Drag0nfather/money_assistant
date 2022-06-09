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
    payment_date = models.DateField()

    def __str__(self):
        return self.username
