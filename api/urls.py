from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import CategoryViewSet, SpendItemViewSet

router = DefaultRouter()

router.register('category', CategoryViewSet)
router.register('spenditem', SpendItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('addcategory/', CategoryViewSet.as_view({'post': 'add_category'})),
    path('showmonth/', CategoryViewSet.as_view({'post': 'show_month_category_balance'}))
]
