from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import CustomUser
from .serializers import UsersShowSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UsersShowSerializer

    def set_limit(self, request):
        data = request.data
        user_id = self.request.user.id
        try:
            CustomUser.objects.filter(id=user_id).update(money=data['limit'])
            return Response({'money update to': data['limit']}, status=status.HTTP_200_OK)
        except:
            return Response(
                {'status': 'Не передан лимит трат'},
                status=status.HTTP_404_NOT_FOUND
            )

    def me(self, request):
        query = CustomUser.objects.get(id=self.request.user.id)
        serializer = UsersShowSerializer(query)
        return Response(serializer.data)

    def set_payment_date(self, request):
        data = request.data
        user_id = self.request.user.id
        try:
            CustomUser.objects.filter(id=user_id).update(payment_date=data['payment_date'])
            return Response(data={'payment date changes': data['payment_date']}, status=status.HTTP_200_OK)
        except:
            return Response(
                {'status': 'Не передана дата платежа'},
                status=status.HTTP_404_NOT_FOUND
            )
