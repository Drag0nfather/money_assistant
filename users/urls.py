from django.urls import path, include
from rest_framework.routers import DefaultRouter


from users.views import UserViewSet

router = DefaultRouter()

router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('setlimit', UserViewSet.as_view({'post': 'set_limit'}))
]
