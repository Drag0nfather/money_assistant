from django.shortcuts import render
from rest_framework import viewsets
from .models import Category, UserCategory, SpendItem
from .serializers import CategorySerializer, UserCategorySerializer, SpendItemSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class UserCategoryViewSet(viewsets.ModelViewSet):
    queryset = UserCategory.objects.all()
    serializer_class = UserCategorySerializer


class SpendItemViewSet(viewsets.ModelViewSet):
    queryset = SpendItem.objects.all()
    serializer_class = SpendItemSerializer
