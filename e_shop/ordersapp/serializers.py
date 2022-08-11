from rest_framework import serializers
from django.db import transaction

from basketapp.models import Basket
from ordersapp.models import *


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = '__all__'


class CustomerDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerData
        fields = '__all__'


class DeliverySerializer(serializers.ModelSerializer):

    class Meta:
        model = Delivery
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('item', 'quantity', 'price')


class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = ('customer_data', 'comment', 'organization', 'pickup_shop', 'delivery', 'payment_type', 'items')

    def save(self, **kwargs):
        user = self.context.get('request').user

        orderitems_data = self.validated_data.get('items')
        if isinstance(orderitems_data, list):
            self.validated_data.pop('items')

        if vars(user):
            basket: Basket = user.basket
            with transaction.atomic():
                order = super().save(**kwargs)

                basketitems = basket.itembasket_set.select_related('item')
                if basketitems.count() == 0:
                    raise ValidationError('Нет товаров в корзине')

                for el in basketitems:
                    OrderItem.objects.create(order=order, item=el.item, quantity=el.quantity)
                basket.clear()
        else:
            with transaction.atomic():
                order = super().save(**kwargs)
                if orderitems_data:
                    for el in orderitems_data:
                        OrderItem.objects.create(order=order, item=el.get('item'), quantity=el.get('quantity'))
                else:
                    raise ValidationError('Нет товаров в корзине')
        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False, source='orderitem_set')
    customer_data = CustomerDataSerializer()
    organization = OrganizationSerializer(required=False)
    # TODO
    # pickup_shop = 
    delivery = DeliverySerializer(required=False)

    class Meta:
        model = Order
        fields = ('customer_data', 'comment', 'organization', 'pickup_shop', 'delivery', 'payment_type', 'items')
