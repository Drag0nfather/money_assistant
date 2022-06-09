from rest_framework import serializers
from .models import CustomUser


class UsersShowSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'username', 'name', 'email', 'money', 'payment_date')
        model = CustomUser
