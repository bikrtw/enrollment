import enum

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


class ShopUnit(ShopUnitABS):
    """
    Товар, категория
    """
    id = models.TextField(primary_key=True, max_length=36)
    _price = models.IntegerField(null=True)
    parent = models.ForeignKey(
        to='ShopUnit',
        on_delete=models.CASCADE,
        related_name='children',
        null=True
    )

    @property
    def price(self):
        if self.type == ShopUnitType.CATEGORY.value:
            return self.get_category_price()
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    def get_category_price(self):
        parent_category_ids = [self.id]
        child_prices = []
        while parent_category_ids:
            current_id = parent_category_ids.pop()
            children = self.__class__.objects.filter(parent__id=current_id)
            [child_prices.append(e.price)
             for e in children
             if e.type == ShopUnitType.OFFER.value]
            [parent_category_ids.append(e.id)
             for e in children
             if e.type == ShopUnitType.CATEGORY.value]
        if child_prices:
            return sum(child_prices) / len(child_prices)
        return None

    def __str__(self):
        return f'[{self.id}] {self.type}: {self.name} - {self.price}'


class ShopUnitStatisticUnit(ShopUnitABS):
    """
    История изменений товара
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'source'],
                                    name='unique_update')
        ]

    price = models.IntegerField(null=True)

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
        return f'[{self.source.id}] {self.name}: {self.price}'


@receiver(post_save, sender=ShopUnit)
def post_save_handler(sender, instance, created, **kwargs):
    """
    Обработчик пост-сохранения - добавляем запись в историю
    """
    obj, _ = ShopUnitStatisticUnit.objects.get_or_create(
        date=instance.date,
        source=instance,
        defaults={'name': instance.name,
                  'type': instance.type,
                  'parent': instance.parent}
    )
    obj.price = instance.price
    obj.save()


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
