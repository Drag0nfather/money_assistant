from datetime import date, datetime

from rest_framework.response import Response
from rest_framework import viewsets, status

from users.models import CustomUser
from .models import Category, SpendItem
from .serializers import CategorySerializer, SpendItemSerializer, DayCategorySerializer, MonthCategorySerializer


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
        if not data.get('category_name') and not data.get('limit'):
            return Response(
                {'status': 'Не передана категория и лимит трат'},
                status=status.HTTP_404_NOT_FOUND
            )
        elif not data.get('category_name'):
            return Response(
                {'status': 'Не передана категория'},
                status=status.HTTP_404_NOT_FOUND
            )
        elif not data.get('limit'):
            return Response(
                {'status': 'Не передан лимит трат'},
                status=status.HTTP_404_NOT_FOUND
            )

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
                fact_spend=0,
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
        try:
            category = user_categories.get(category_name=data['category_name'])
            category.delete()
            return Response({'Удалена категория': category.category_name}, status=status.HTTP_200_OK)
        except:
            return Response(
                {'status': f'Категории {data["category_name"]} не существует'},
                status=status.HTTP_404_NOT_FOUND
            )

    def show_month_category_balance(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        user_categories = Category.objects.filter(user=user_object)
        if data.get('category_name'):
            single_category = user_categories.get(category_name=data['category_name'])
            serializer = MonthCategorySerializer(single_category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = MonthCategorySerializer(user_categories, many=True)
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
            serializer = DayCategorySerializer(single_category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            for category in user_categories:
                day_balance = category.limit / days_delta
                category.limit = day_balance
            serializer = DayCategorySerializer(user_categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class SpendItemViewSet(viewsets.ModelViewSet):
    queryset = SpendItem.objects.all()
    serializer_class = SpendItemSerializer

    def add_spend_item(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)

        # Берем остаток в категории и прибавляем потраченное
        category = Category.objects.filter(user=user_object).get(category_name=data['category'])
        sum_spend = category.fact_spend + int(data['cost'])

        # Обновляем поле остатка в категории
        Category.objects.filter(
            user=user_object).filter(
            category_name=data['category']).update(
            fact_spend=sum_spend
        )

        # Уменьшаем сумму бюджета на количество потраченного
        money = CustomUser.objects.get(id=user_id).money
        new_money = money - int(data['cost'])
        CustomUser.objects.filter(
            id=user_id).update(
            money=new_money
        )

        # Создание объекта траты
        # TODO datetime.now выдает неправильное время
        if not data.get('date'):
            SpendItem.objects.create(
                amount=data['cost'],
                category=category,
                date=datetime.now(),
            )
        else:
            SpendItem.objects.create(
                amount=data['cost'],
                category=category,
                date=data['date'],
            )
        cost = data['cost']
        return Response({f'Трата в категории {category.category_name}': f'{cost} р.'})

    def show_spend_items(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        if data.get('category'):
            spend_items = SpendItem.objects.filter(
                category__user=user_object).filter(
                category__category_name=data['category']
            )
            serializer = SpendItemSerializer(spend_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            spend_items = SpendItem.objects.filter(category__user=user_object)
            serializer = SpendItemSerializer(spend_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_spend_item(self, request):
        data = request.data
        user_id = self.request.user.id
        user_spend_items = SpendItem.objects.filter(category__user=user_id)
        try:
            spend_item = user_spend_items.get(id=data['item_id'])

            # Увеличиваем сумму бюджета на количество в удаленной трате
            money = CustomUser.objects.get(id=user_id).money
            new_money = money + spend_item.amount
            CustomUser.objects.filter(
                id=user_id).update(
                money=new_money
            )

            spend_item.delete()
            return Response(
                {f'Удалено {spend_item.amount} р. в категории {spend_item.category.category_name}': 'ok'},
                status=status.HTTP_200_OK
            )
        except:
            return Response(
                {f'Не найдено указанной траты': request.data},
                status=status.HTTP_404_NOT_FOUND
            )
