from datetime import datetime

from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import Category
from api.views import update_day_balance
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
            CustomUser.objects.filter(id=user_id).update(period_begin_money=data['limit'])
        except:
            return Response(
                {'status': 'Не передан лимит трат'},
                status=status.HTTP_404_NOT_FOUND
            )
        if data.get('start_date'):
            if type(datetime.strptime(data['date'], '%Y-%m-%d %H:%M')) == datetime:
                CustomUser.objects.filter(id=user_id).update(start_date=data['start_date'])
                update_user_day_balance(user_id)
                return Response(
                    {
                        'money update to': data['limit'],
                        'start_date': data['start_date']
                    }
                    , status=status.HTTP_200_OK)
            else:
                return Response({'error': 'передано время в неверном формате'}, status=status.HTTP_404_NOT_FOUND)
        else:
            now = datetime.now().strftime('%Y-%m-%d')
            CustomUser.objects.filter(id=user_id).update(start_date=now)
            update_user_day_balance(user_id)
            return Response(
                {
                    'money update to': data['limit'],
                    'start_date': now
                }
                , status=status.HTTP_200_OK)

    def me(self, request):
        update_day_balance(self.request.user.id)
        query = CustomUser.objects.get(id=self.request.user.id)
        serializer = UsersShowSerializer(query)
        return Response(serializer.data)

    def set_payment_date(self, request):
        data = request.data
        user_id = self.request.user.id
        try:
            CustomUser.objects.filter(id=user_id).update(end_date=data['payment_date'])
        except:
            return Response(
                {'status': 'Не передана дата платежа'},
                status=status.HTTP_404_NOT_FOUND
            )
        update_user_day_balance(user_id)
        reset_fact_spend_in_categories(user_id)
        return Response(data={'payment date changes': data['payment_date']}, status=status.HTTP_200_OK)


def update_user_day_balance(user_id):
    user_object = CustomUser.objects.get(id=user_id)
    user_money = user_object.money
    today = datetime.now()
    user_payment_day = user_object.end_date
    user_payment_day_in_datetime = datetime(
        year=user_payment_day.year,
        month=user_payment_day.month,
        day=user_payment_day.day
    )
    days_delta = (user_payment_day_in_datetime - today).days + 1
    money_remainder = round(user_money / days_delta, 2)
    CustomUser.objects.filter(id=user_id).update(day_balance=money_remainder)


def reset_fact_spend_in_categories(user_id):
    user_object = CustomUser.objects.get(id=user_id)
    user_categories = Category.objects.filter(user=user_object)
    for category in user_categories:
        category.fact_spend = 0
        category.save()
