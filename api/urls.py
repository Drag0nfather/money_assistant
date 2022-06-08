from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import CategoryViewSet, UserCategoryViewSet, SpendItemViewSet

router = DefaultRouter()

router.register('category', CategoryViewSet)
router.register('usercategory', UserCategoryViewSet)
router.register('spenditem', SpendItemViewSet)

urlpatterns = [
    path('', include(router.urls))
]
