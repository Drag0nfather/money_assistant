from datetime import date, datetime

from rest_framework.response import Response
from rest_framework import viewsets, status

from users.models import CustomUser
from .models import Category, SpendItem
from .serializers import CategorySerializer, SpendItemSerializer, MonthCategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = self.queryset
        query = queryset.filter(user=self.request.user)
        return query

    def add_category(self, request):
        data = request.data
        user_id = request.auth.payload['user_id']
        user_object = CustomUser.objects.get(id=user_id)

        similar_category = Category.objects.filter(
            category_name=data['category_name']).filter(
            limit=data['limit']).filter(user=user_object)
        if similar_category:
            return Response(
                data={'Уже имеется категория с таким лимитом': data['category_name']},
                status=status.HTTP_200_OK
            )

        other_limit_category = Category.objects.filter(
            category_name=data['category_name']).filter(user=user_object)
        if other_limit_category:
            Category.objects.update(limit=data['limit'])
            category_name = data['category_name']
            return Response(
                data={f'Обновлен лимит у категории {category_name}': data['limit']},
                status=status.HTTP_201_CREATED
            )
        else:
            Category.objects.create(
                category_name=data['category_name'],
                limit=data['limit'],
                user=user_object
            )
            return Response(
                data={'Добавлена категория': data['category_name']},
                status=status.HTTP_200_OK
            )

    def show_month_category_balance(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        user_categories = Category.objects.filter(user=user_object)
        single_category = user_categories.get(category_name=data['category_name'])
        serializer = MonthCategorySerializer(single_category)
        return Response(serializer.data)

    def show_day_category_balance(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        user_categories = Category.objects.filter(user=user_object)
        single_category = user_categories.get(category_name=data['category_name'])
        today = datetime.now()
        user_payment_day = user_object.payment_date
        user_payment_day_in_datetime = datetime(
            year=user_payment_day.year,
            month=user_payment_day.month,
            day=user_payment_day.day
        )
        days_delta = (user_payment_day_in_datetime-today).days
        day_balance = single_category.limit / days_delta
        single_category.limit = day_balance
        serializer = MonthCategorySerializer(single_category)
        return Response(serializer.data)


class SpendItemViewSet(viewsets.ModelViewSet):
    queryset = SpendItem.objects.all()
    serializer_class = SpendItemSerializer
