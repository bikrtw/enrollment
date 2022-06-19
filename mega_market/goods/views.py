import datetime
from http import HTTPStatus

from dateutil.parser import isoparse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from .models import ShopUnit, update_category_prices, update_parents_date, \
    ShopUnitType, ShopUnitStatisticUnit
from .serializers import ShopUnitSerializer, ShopUnitStatisticUnitSerializer
from .throttle import GetModifyRateThrottle, GetReadRateThrottle


@api_view(['GET'])
@throttle_classes([GetReadRateThrottle])
def nodes(request, node_id):
    """
    Возвращает элемент по id
    """

    node = get_object_or_404(ShopUnit, id=node_id)
    serializer = ShopUnitSerializer(node)
    return Response(serializer.data, status=HTTPStatus.OK)


@api_view(['GET'])
@throttle_classes([GetReadRateThrottle])
def sales(request):
    """
    Возвращает список продаж за последние сутки
    """
    try:
        date = isoparse(request.query_params.get('date'))
    except (ValueError, TypeError):
        raise ParseError('Incorrect date format')

    sales = ShopUnit.objects.filter(
        type=ShopUnitType.OFFER.value
    ).filter(
        date__gte=(date - datetime.timedelta(days=1))
    ).filter(
        date__lte=date
    )
    serializer = ShopUnitSerializer(sales, many=True)
    return Response({'items': serializer.data}, status=HTTPStatus.OK)


@api_view(['GET'])
@throttle_classes([GetReadRateThrottle])
def get_node_statistic(request, node_id):
    """
    Возвращает статистику по элементу - не доделано
    """
    date_from = request.query_params.get('dateStart')
    date_to = request.query_params.get('dateEnd')
    try:
        if date_from:
            date_from = isoparse(date_from)
        if date_to:
            date_to = isoparse(date_to)
    except ValueError:
        raise ParseError('Incorrect date format')

    queryset = ShopUnitStatisticUnit.objects.filter(source_id=node_id)
    if date_from:
        queryset = queryset.filter(date__gte=date_from)
    if date_to:
        queryset = queryset.filter(date__lte=date_to)
    serializer = ShopUnitStatisticUnitSerializer(queryset, many=True)
    return Response({'items': serializer.data}, status=HTTPStatus.OK)


@api_view(['POST'])
@throttle_classes([GetModifyRateThrottle])
def imports(request):
    """
    Импортирует данные по нодам из запроса
    """

    data = request.data
    updated = data.get('updateDate')
    created = []
    ids = set()
    for node in data.get('items'):
        node['date'] = updated

        # Проверяем уникальность нод в запросе
        if node['id'] in ids:
            [item.delete() for item in created]
            raise ParseError('Duplicate id')
        ids.add(node['id'])

        # Возвращает существующий нод или None
        item = ShopUnit.objects.filter(id=node['id']).first()

        # Если тип существующего нода и тип пришедшего не совпадают
        if item and item.type != node['type']:
            [item.delete() for item in created]
            raise ParseError()

        serializer = ShopUnitSerializer(item, data=node)

        if not serializer.is_valid():
            [item.delete() for item in created]
            raise ParseError(serializer.errors)

        created.append(serializer.save())

    update_category_prices()
    update_parents_date(list(ids), updated)

    return Response(status=HTTPStatus.OK)


@api_view(['GET', 'DELETE'])  # get to allow postman to test delete
@throttle_classes([GetModifyRateThrottle])
def delete(request, node_id):
    """
    Удаляет элемент по id
    """

    node = get_object_or_404(ShopUnit, id=node_id)
    node.delete()

    update_category_prices()
    return Response(status=HTTPStatus.OK)
