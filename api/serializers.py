from rest_framework import serializers
from .models import Category, SpendItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'category_name', 'limit', 'user')
        model = Category


class DayAndMonthCategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'category_name', 'limit', 'fact_spend')
        model = Category


class CategoryInSpendItemSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('category_name',)
        model = Category


class SpendItemSerializer(serializers.ModelSerializer):
    category = CategoryInSpendItemSerializer(read_only=True)

    class Meta:
        fields = ('id', 'amount', 'category')
        model = SpendItem
