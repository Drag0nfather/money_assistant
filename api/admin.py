from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Category, UserCategory, SpendItem

admin.site.register(Category)
admin.site.register(UserCategory)
admin.site.register(SpendItem)
