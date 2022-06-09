from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UsersShowSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersShowSerializer

    def set_limit(self, request):
        data = request.data
        user_id = request.auth.payload['user_id']
        CustomUser.objects.filter(id=user_id).update(money=data['limit'])
        return Response(data={'money update to': data['limit']}, status=status.HTTP_200_OK)

    def me(self, request):
        query = CustomUser.objects.get(id=self.request.user.id)
        serializer = UsersShowSerializer(query)
        return Response(serializer.data)
