import enum
from collections import defaultdict

from django.db import models


class ShopUnitType(enum.Enum):
    """
    Типы сущностей в магазине
    """
    OFFER = 'OFFER'
    CATEGORY = 'CATEGORY'

    @classmethod
    def choices(cls):
        return tuple((e.name, e.value) for e in cls)


class ShopUnitABS(models.Model):

    class Meta:
        abstract = True

    id = models.TextField(primary_key=True, max_length=36)
    name = models.TextField(max_length=255)
    date = models.DateTimeField()
    type = models.TextField(choices=ShopUnitType.choices(), max_length=8)
    price = models.IntegerField(null=True)

    def __str__(self):
        return self.name


class ShopUnit(ShopUnitABS):
    """
    Товар, категория
    """
    parent_id = models.ForeignKey(
        to='ShopUnit',
        on_delete=models.CASCADE,
        related_name='children',
        null=True
    )


def update_category_prices():
    """
    Обновляет цены в категориях
    """

    elements = ShopUnit.objects.filter(type=ShopUnitType.OFFER.value)

    categories = ShopUnit.objects.filter(type=ShopUnitType.CATEGORY.value)

    elements = {e.id:
                {'parent_id': e.parent_id, 'price': e.price, 'type': e.type}
                for e in elements}

    category_prices = defaultdict(list)

    for e in elements.values():
        parent = e['parent_id']
        while parent:
            category_prices[parent.id].append(e['price'])
            parent = parent.parent_id

    for category in categories:
        category.price = (sum(category_prices[category.id])
                          / len(category_prices[category.id]))
        category.save()


def update_parents_date(ids, date):
    """
    Обновляет дату изменения для родительских элементов
    """

    ids_to_update = ids

    while ids_to_update:
        elements = ShopUnit.objects.filter(id__in=ids_to_update)
        ids_to_update = []
        for element in elements:
            element.date = date
            if element.parent_id:
                ids_to_update.append(element.parent_id.id)
            element.save()
