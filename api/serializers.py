from rest_framework import serializers
from .models import Category, SpendItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'category_name', 'limit', 'user')
        model = Category


class MonthCategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'category_name', 'limit', 'fact_spend')
        model = Category

class DayCategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'category_name', 'limit')
        model = Category


class SpendItemSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.category_name')
    class Meta:
        fields = ('id', 'amount', 'category', 'date')
        model = SpendItem
