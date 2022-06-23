from dateutil.parser import isoparse
from rest_framework import serializers

from .models import ShopUnit, ShopUnitType, ShopUnitStatisticUnit


class ISO8601DateField(serializers.Field):
    """
    Преобразует дату в формат ISO 8601
    """

    def to_representation(self, value):
        return value.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    def to_internal_value(self, data):
        try:
            return isoparse(data)
        except ValueError:
            raise serializers.ValidationError(f'Incorrect date format')


class ShopUnitSerializer(serializers.ModelSerializer):
    parentId = serializers.PrimaryKeyRelatedField(
        queryset=ShopUnit.objects,
        source='parent',
        required=False,
        allow_null=True
    )

    price = serializers.IntegerField(required=False, allow_null=True)

    date = ISO8601DateField()

    class Meta:
        model = ShopUnit
        fields = (
            'id', 'name', 'type', 'parentId', 'date', 'price')

    def get_children(self, obj):
        if obj.type == ShopUnitType.CATEGORY.value:
            return ShopUnitSerializer(
                obj.children, many=True, read_only=True).data
        else:
            return None

    def validate_price(self, value):
        if self.initial_data['type'] == ShopUnitType.OFFER.value:
            if value is None or value < 0:
                raise serializers.ValidationError('Price must be positive')
        if (self.initial_data['type'] == ShopUnitType.CATEGORY.value
                and value is not None):
            raise serializers.ValidationError('Price must be null')
        return value

    def validate_parentId(self, value):
        if value:
            if value.type != ShopUnitType.CATEGORY.value:
                raise serializers.ValidationError(
                    'Parent must be existing category')
            if value.id == self.initial_data['id']:
                raise serializers.ValidationError(
                    'Parent must be different from current')
        return value


class ShopUnitStatisticUnitSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='source', read_only=True)
    parentId = serializers.PrimaryKeyRelatedField(
        source='parent', read_only=True)
    date = ISO8601DateField()

    class Meta:
        model = ShopUnitStatisticUnit
        fields = ['id', 'name', 'date', 'price', 'type', 'parentId']
