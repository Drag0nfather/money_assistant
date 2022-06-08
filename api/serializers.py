from rest_framework import serializers
from .models import Category, UserCategory, SpendItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'category_name', 'limit')
        model = Category


class UserCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'category', 'user')
        model = UserCategory


class SpendItemSerializer(serializers.ModelSerializer):
    category = UserCategorySerializer(read_only=True)

    class Meta:
        fields = ('id', 'amount', 'category')
        model = SpendItem
