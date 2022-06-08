from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UsersShowSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersShowSerializer

    def set_limit(self, request):
        user_obj = CustomUser.objects.filter(id=request.id).update(money=request.money)
        user_obj.save()
        return Response(data=request.money, status=status.HTTP_200_OK)
