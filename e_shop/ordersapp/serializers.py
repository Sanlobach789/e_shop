from rest_framework import serializers

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


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'
        