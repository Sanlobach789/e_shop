from rest_framework import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404

from adminapp.serializers import ShopSerializer
from basketapp.models import Basket
from ordersapp.models import *


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'

    def create(self, validated_data):
        validated_data['user'] = self.context.get('user')
        return super().create(validated_data)


class CustomerDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerData
        fields = ('name', 'phone_number', 'email', 'user')


class DeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('item', 'quantity', 'price')


class CreateOrderSerializer(serializers.ModelSerializer):
    customer_data = CustomerDataSerializer(required=True)

    class Meta:
        model = Order
        fields = ('customer_data', 'comment', 'organization', 'pickup_shop', 'delivery', 'payment_type')

    def create(self, validated_data):
        # Создание `customer_data`, инчае ошибка выскакивает, что нельзя создать вложенный объект.
        validated_data['customer_data']['user'] = self.context.get('request').user.pk
        customer_data_serializer = CustomerDataSerializer(data=validated_data.get('customer_data'))
        customer_data_serializer.is_valid(raise_exception=True)
        customer_data = customer_data_serializer.save()
        validated_data['customer_data'] = customer_data
        return super().create(validated_data)

    def save(self, **kwargs):
        # Получение пользователя, который создает заказ
        user = self.context.get('request').user

        # Если пользователь автирозован, то ...
        if vars(user):
            # ... просто берем его корзину
            basket: Basket = user.basket
        else:
            # ... пытаемся получить корзину
            basket: Basket = get_object_or_404(Basket, pk=self.context.get('request').headers.get('Basket'))

        with transaction.atomic():
            order = super().save(**kwargs)

            basketitems = basket.itembasket_set.select_related('item')
            # Проверяем, что корзина не пустая
            if basketitems.count() == 0:
                raise ValidationError('Нет товаров в корзине')

            # Переносим товары из корзины в заказ
            for el in basketitems:
                OrderItem.objects.create(order=order, item=el.item, quantity=el.quantity)
            # Очищаем корзину
            basket.clear()

        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False, source='orderitem_set')
    customer_data = CustomerDataSerializer()
    organization = OrganizationSerializer(required=False)
    pickup_shop = ShopSerializer(required=False)
    delivery = DeliverySerializer(required=False)

    class Meta:
        model = Order
        fields = ('customer_data', 'comment', 'organization', 'pickup_shop', 'delivery', 'payment_type', 'items')


class ActionStatusOrderSerializer(serializers.Serializer):
    """"Сериализатор изменения статуса заказа"""


class StatusOrderSerializer(serializers.ModelSerializer):
    """"Сериализатор статуса заказа"""
    class Meta:
        model = Order
        fields = ('pk', 'status')
