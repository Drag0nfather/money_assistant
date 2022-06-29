from datetime import datetime

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
        except:
            return Response(
                {'status': f'Категории {data["category_name"]} не существует'},
                status=status.HTTP_404_NOT_FOUND
            )
        all_spend_items = SpendItem.objects.filter(category_id=category.id)
        if data.get('is_return'):
            if data['is_return'] == 'all_period':
                sum_spend = 0
                for spend_item in all_spend_items:
                    sum_spend += spend_item.amount
                    spend_item.delete()
                    spend_item.save()
                money = CustomUser.objects.get(id=user_id).money
                period_begin_money = CustomUser.objects.get(id=user_id).period_begin_money
                new_money = money + sum_spend
                new_period_begin_money = period_begin_money + sum_spend
                CustomUser.objects.filter(id=user_id).update(money=new_money)
                CustomUser.objects.filter(id=user_id).update(period_begin_money=new_period_begin_money)
                category.delete()
                return Response(
                    {
                        'Все объекты трат в этой категории удалены, на баланс возвращено:':
                            f'{sum_spend} р.'
                    },
                    status=status.HTTP_200_OK
                )
            elif data['is_return'] == 'custom':
                start_date = data.get('date_start')
                end_date = data.get('date_end')
                all_spend_items.filter(date__range=[start_date, end_date])
                sum_spend = 0
                for spend_item in all_spend_items:
                    sum_spend += spend_item.amount
                    spend_item.delete()
                    spend_item.save()
                money = CustomUser.objects.get(id=user_id).money
                period_begin_money = CustomUser.objects.get(id=user_id).period_begin_money
                new_money = money + sum_spend
                new_period_begin_money = period_begin_money + sum_spend
                CustomUser.objects.filter(id=user_id).update(money=new_money)
                CustomUser.objects.filter(id=user_id).update(period_begin_money=new_period_begin_money)
                category.delete()
                return Response(
                    {
                        'Все объекты трат в этой категории удалены, на баланс возвращено:':
                            f'{sum_spend} р.'
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response({'error': 'Передан неверный период для удаления'}, status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response({'Удалена категория': category.category_name}, status=status.HTTP_200_OK)


    def show_day_balance(self, request):
        user_id = request.user.id
        update_day_balance(user_id)
        day_balance = CustomUser.objects.get(id=self.request.user.id).day_balance
        return Response({'остаток на день': f'{day_balance} р.'}, status=status.HTTP_200_OK)

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
        days_delta = (user_payment_day_in_datetime - today).days + 1
        if data.get('category_name'):
            try:
                single_category = user_categories.get(category_name=data['category_name'])
            except:
                return Response(
                    {'Не найдено категории':
                         data.get('category_name')
                     },
                    status=status.HTTP_400_BAD_REQUEST)
            day_balance = single_category.limit / days_delta
            today_min = datetime.combine(datetime.today().date(), datetime.today().time().min)
            today_max = datetime.combine(datetime.today().date(), datetime.today().time().max)
            today_spend_items = SpendItem.objects.filter(
                category__user=user_id).filter(
                category=single_category).filter(
                date__range=(
                    today_min,
                    today_max
                ))
            sum_spend = 0
            for spend_item in today_spend_items:
                sum_spend += spend_item.amount
            limit = day_balance - sum_spend
            if limit < 0:
                single_category.limit = 0
            else:
                single_category.limit = day_balance - sum_spend
            serializer = DayCategorySerializer(single_category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            for category in user_categories:
                day_balance = category.limit / days_delta
                today_min = datetime.combine(datetime.today().date(), datetime.today().time().min)
                today_max = datetime.combine(datetime.today().date(), datetime.today().time().max)
                today_spend_items = SpendItem.objects.filter(
                    category__user=user_id).filter(
                    category=category).filter(
                    date__range=(
                        today_min,
                        today_max
                    ))
                sum_spend = 0
                for spend_item in today_spend_items:
                    sum_spend += spend_item.amount
                limit = day_balance - sum_spend
                if limit < 0:
                    category.limit = 0
                else:
                    category.limit = day_balance - sum_spend
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
        try:
            category = Category.objects.filter(user=user_object).get(category_name=data.get('category'))
        except:
            return Response(
                {'Передана неверная категория': data.get('category')},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            sum_spend = category.fact_spend + int(data.get('cost'))
        except:
            return Response(
                {'error': 'Не передано количество'},
                status=status.HTTP_404_NOT_FOUND
            )

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
        date_today = datetime.now()
        if not data.get('date'):
            SpendItem.objects.create(
                amount=data['cost'],
                category=category,
                date=date_today,
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
                category__category_name=data.get('category')
            ).order_by('-id')
            if len(spend_items) == 0:
                return Response(
                    {'Не найдено трат в указанной категории, либо категория неверна': data.get('category')},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = SpendItemSerializer(spend_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif data.get('item_id'):
            try:
                spend_item = SpendItem.objects.get(id=data.get('item_id'))
            except:
                return Response(
                    {'Не найдено указанной траты': data.get('item_id')},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = SpendItemSerializer(spend_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            spend_items = SpendItem.objects.filter(category__user=user_object).order_by('-id')
            serializer = SpendItemSerializer(spend_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_spend_item(self, request):
        data = request.data
        user_id = self.request.user.id
        user_spend_items = SpendItem.objects.filter(category__user=user_id)
        user_object = CustomUser.objects.get(id=user_id)
        try:
            spend_item = user_spend_items.get(id=data['item_id'])

            # Увеличиваем сумму бюджета на количество в удаленной трате
            money = CustomUser.objects.get(id=user_id).money
            new_money = money + spend_item.amount
            CustomUser.objects.filter(
                id=user_id).update(
                money=new_money
            )
            # Уменьшаем фактически потраченное в категории
            spend_item_category = spend_item.category.category_name
            category_money = Category.objects.filter(user=user_object).get(category_name=spend_item_category).fact_spend
            new_money = category_money - spend_item.amount
            Category.objects.filter(category_name=spend_item_category).update(fact_spend=new_money)
            # Удаляем объект траты
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

    def change_spend_item(self, request):
        data = request.data
        user_id = self.request.user.id
        user_object = CustomUser.objects.get(id=user_id)
        try:
            spend_item_query = SpendItem.objects.filter(id=data.get('item_id'))
            spend_item_obj = SpendItem.objects.get(id=data.get('item_id'))
        except:
            return Response(
                {'Не найдена трата': data.get('item_id')},
                status=status.HTTP_404_NOT_FOUND
            )
        if data.get('amount'):
            # Обновляем сумму бюджета на количество в измененной трате
            money = CustomUser.objects.get(id=user_id).money
            new_money = money - spend_item_obj.amount + int(data['amount'])
            CustomUser.objects.filter(
                id=user_id).update(
                money=new_money
            )
            # Обновляем количество фактически потраченного в категории
            spend_item_category = spend_item_obj.category.category_name
            category_money = Category.objects.filter(user=user_object).get(category_name=spend_item_category).fact_spend
            new_money = category_money - spend_item_obj.amount + category_money
            Category.objects.filter(category_name=spend_item_category).update(fact_spend=new_money)
            # Обновляем поле количества
            spend_item_query.update(amount=data['amount'])
            return Response(
                {f'Трата {spend_item_obj.id} изменена': f'{data["amount"]} р.'},
                status=status.HTTP_200_OK
            )
        elif data.get('category'):
            # Уменьшаем количество потраченного в старой категории
            old_category = spend_item_obj.category.category_name
            old_category_money = Category.objects.filter(user=user_object).get(category_name=old_category).fact_spend
            new_category_money = old_category_money - spend_item_obj.amount
            Category.objects.filter(user=user_object).filter(category_name=old_category).update(fact_spend=new_category_money)

            # Увеличиваем количество потраченного в новой категории
            try:
                new_category = data.get('category')
                old_category_money = Category.objects.filter(user=user_object).get(category_name=new_category).fact_spend
                new_category_money = old_category_money + spend_item_obj.amount
                Category.objects.filter(user=user_object).filter(category_name=new_category).update(fact_spend=new_category_money)
            except:
                # Если не найдена категория - возвращаем баланс старой категории
                old_category_money = Category.objects.filter(user=user_object).get(category_name=old_category).fact_spend
                new_category_money = old_category_money - spend_item_obj.amount
                Category.objects.filter(user=user_object).filter(category_name=old_category).update(fact_spend=new_category_money)
                return Response(
                    {'Не найдена указанная категория': data.get('category')},
                    status=status.HTTP_404_NOT_FOUND
                )
            # Присваиваем трате новую категорию
            try:
                new_category = Category.objects.filter(user_id=user_id).get(category_name=data.get('category'))
            except:
                return Response({'Не найдена категория': data.get('category')}, status=status.HTTP_404_NOT_FOUND)
            spend_item_query.update(category=new_category.id)
            return Response({f'Трате {spend_item_obj.id} присвоена новая категория': data.get('category')}, status=status.HTTP_200_OK)
        elif data['date']:
            if data['date'] == 'nothing':
                now = datetime.now().strftime('%Y-%m-%d %H:%M')
                spend_item_query.update(date=now)
                return Response({f'Изменена дата у категории {spend_item_obj.id}': now}, status=status.HTTP_200_OK)

            elif type(datetime.strptime(data['date'], '%Y-%m-%d %H:%M')) == datetime:
                spend_item_query.update(date=data.get('date'))
                return Response({f'Изменена дата у категории {spend_item_obj.id}': data.get('date')},
                                status=status.HTTP_200_OK)
            else:
                return Response({'error': 'передано время в неверном формате'}, status=status.HTTP_404_NOT_FOUND)


def update_day_balance(user_id):
    user_object = CustomUser.objects.get(id=user_id)
    user_money = user_object.period_begin_money
    today = datetime.now()
    user_payment_day = user_object.payment_date
    user_payment_day_in_datetime = datetime(
        year=user_payment_day.year,
        month=user_payment_day.month,
        day=user_payment_day.day
    )
    days_delta = (user_payment_day_in_datetime - today).days + 1
    money_remainder = round(user_money / days_delta, 2)
    today_min = datetime.combine(datetime.today().date(), datetime.today().time().min)
    today_max = datetime.combine(datetime.today().date(), datetime.today().time().max)
    today_spend_items = SpendItem.objects.filter(category__user=user_id).filter(date__range=(today_min, today_max))
    sum_spend = 0
    for spend_item in today_spend_items:
        sum_spend += spend_item.amount
    new_money = money_remainder - sum_spend
    CustomUser.objects.filter(id=user_id).update(day_balance=new_money)
