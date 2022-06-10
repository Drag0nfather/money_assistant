from datetime import date, datetime

from rest_framework.response import Response
from rest_framework import viewsets, status

from users.models import CustomUser
from .models import Category, SpendItem
from .serializers import CategorySerializer, SpendItemSerializer, DayAndMonthCategorySerializer


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

    def delete_category(self, request):
        data = request.data
        user_id = self.request.user.id
        user_categories = Category.objects.filter(user=user_id)
        category = user_categories.get(category_name=data['category_name'])
        category.delete()
        return Response({'Удалена категория': category.category_name}, status=status.HTTP_200_OK)

    def show_month_category_balance(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        user_categories = Category.objects.filter(user=user_object)
        if data.get('category_name'):
            single_category = user_categories.get(category_name=data['category_name'])
            serializer = DayAndMonthCategorySerializer(single_category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = DayAndMonthCategorySerializer(user_categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def show_day_category_balance(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        user_categories = Category.objects.filter(user=user_object)
        today = datetime.now()
        user_payment_day = user_object.payment_date
        user_payment_day_in_datetime = datetime(
            year=user_payment_day.year,
            month=user_payment_day.month,
            day=user_payment_day.day
        )
        days_delta = (user_payment_day_in_datetime - today).days
        if data.get('category_name'):
            single_category = user_categories.get(category_name=data['category_name'])
            day_balance = single_category.limit / days_delta
            single_category.limit = day_balance
            serializer = DayAndMonthCategorySerializer(single_category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            for category in user_categories:
                day_balance = category.limit / days_delta
                category.limit = day_balance
            serializer = DayAndMonthCategorySerializer(user_categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class SpendItemViewSet(viewsets.ModelViewSet):
    queryset = SpendItem.objects.all()
    serializer_class = SpendItemSerializer

    def add_spend_item(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        category1 = Category.objects.filter(user=user_object).get(category_name=data['category'])
        sum_spend = category1.fact_spend + data['cost']
        category2 = Category.objects.filter(user=user_object).filter(category_name=data['category'])
        category2.update(fact_spend=sum_spend)
        SpendItem.objects.create(
            amount=data['cost'],
            category=category1
        )
        cost = data['cost']
        return Response({f'Трата в категории {category1.category_name}': f'{cost} р.'})

    def show_spend_items(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        if data.get('category'):
            spend_items = SpendItem.objects.filter(
                category__user=user_object).filter(
                category=data['category']
            )
            serializer = SpendItemSerializer(spend_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            spend_items = SpendItem.objects.filter(category__user=user_object)
            serializer = SpendItemSerializer(spend_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
