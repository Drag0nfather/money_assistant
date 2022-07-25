from rest_framework import serializers
from .models import CustomUser


class UsersShowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'username', 'name', 'email', 'money', 'start_date', 'end_date', 'day_balance', 'period_begin_money')
        model = CustomUser
