from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from .models import Order
from .serializers import (
    CreateOrderSerializer, OrderSerializer
)


class OrderModelViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer: CreateOrderSerializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = OrderSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
