import enum
from collections import defaultdict

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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

    name = models.TextField(max_length=255)
    date = models.DateTimeField()
    type = models.TextField(choices=ShopUnitType.choices(), max_length=8)
    price = models.IntegerField(null=True)

    def __str__(self):
        return f'[{self.id}] {self.name}: {self.price}'


class ShopUnit(ShopUnitABS):
    """
    Товар, категория
    """
    id = models.TextField(primary_key=True, max_length=36)
    parent = models.ForeignKey(
        to='ShopUnit',
        on_delete=models.CASCADE,
        related_name='children',
        null=True
    )


class ShopUnitStatisticUnit(ShopUnitABS):
    """
    История изменений товара
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'source'],
                                    name='unique_update')
        ]

    source = models.ForeignKey(
        to='ShopUnit',
        on_delete=models.CASCADE,
        related_name='history',
    )

    parent = models.ForeignKey(
        to='ShopUnit',
        on_delete=models.CASCADE,
        related_name='history_children',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'[{self.parent}] {self.name}: {self.price}'


@receiver(post_save, sender=ShopUnit)
def post_save_handler(sender, instance, created, **kwargs):
    """
    Обработчик пост-сохранения
    """
    ShopUnitStatisticUnit.objects.get_or_create(
        date=instance.date,
        source=instance,
        defaults={'name': instance.name,
                  'price': instance.price,
                  'type': instance.type,
                  'parent': instance.parent}
    )


def update_category_prices():
    """
    Обновляет цены в категориях
    """

    elements = ShopUnit.objects.filter(type=ShopUnitType.OFFER.value)

    categories = ShopUnit.objects.filter(type=ShopUnitType.CATEGORY.value)

    elements = {e.id:
                    {'parent': e.parent, 'price': e.price, 'type': e.type}
                for e in elements}

    category_prices = defaultdict(list)

    for e in elements.values():
        parent = e['parent']
        while parent:
            category_prices[parent.id].append(e['price'])
            parent = parent.parent

    for category in categories:
        if len(category_prices[category.id]) > 0:
            category.price = sum(category_prices[category.id]) / len(
                category_prices[category.id])
        else:
            category.price = None
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
            if element.parent:
                ids_to_update.append(element.parent.id)
            element.save()
