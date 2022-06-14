from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import CategoryViewSet, SpendItemViewSet

router = DefaultRouter()

router.register('category', CategoryViewSet)
router.register('spenditem', SpendItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('addcategory/', CategoryViewSet.as_view({'post': 'add_category'})),
    path('deletecategory/', CategoryViewSet.as_view({'delete': 'delete_category'})),
    path('showmonth/', CategoryViewSet.as_view({'post': 'show_month_category_balance'})),
    path('showday/', CategoryViewSet.as_view({'post': 'show_day_category_balance'})),
    path('addspenditem/', SpendItemViewSet.as_view({'post': 'add_spend_item'})),
    path('showspenditems/', SpendItemViewSet.as_view({'post': 'show_spend_items'})),
    path('deletespenditem/', SpendItemViewSet.as_view({'delete': 'delete_spend_item'})),
    path('changespenditem/', SpendItemViewSet.as_view({'patch': 'change_spend_item'})),

]
