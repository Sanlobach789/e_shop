from rest_framework import serializers

from basketapp.models import Basket, ItemBasket
from mainapp.serializers import ItemShortSerializer


class ItemBasketSerializer(serializers.ModelSerializer):
    """Сериализатор элемента корзины"""
    item = ItemShortSerializer()
    available_quantity = serializers.SerializerMethodField()

    class Meta:
        model = ItemBasket
        fields = ('item', 'quantity', 'available_quantity')

    def get_available_quantity(self, obj: ItemBasket):
        return obj.item.quantity


class BasketSerializer(serializers.ModelSerializer):
    """Сериализатор корзины"""
    items = ItemBasketSerializer(many=True, source='itembasket_set')

    class Meta:
        model = Basket
        fields = ('id', 'items')


class ItemBasketActionSerializer(serializers.Serializer):
    """Сериализатор добавления и удаления товара в/из корзины"""
    item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class ManyItemBasketActionSerializer(serializers.Serializer):
    """Сериализатор добавления и удаления товаров в/из корзины"""
    items = ItemBasketActionSerializer(many=True)
