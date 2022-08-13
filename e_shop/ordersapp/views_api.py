from http import HTTPStatus

from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from .models import Order
from .serializers import (
    CreateOrderSerializer, OrderSerializer
)


class OrderModelViewSet(viewsets.ReadOnlyModelViewSet,
                        mixins.CreateModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        user = self.request.user
        if vars(user):
            return super().get_queryset().filter(customer_data__user=user)
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'list':
            return [IsAuthenticated()]
        return super().get_permissions()

    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: OrderSerializer,
        HTTPStatus.BAD_REQUEST.value: 'Bad Request',
    })
    def create(self, request, *args, **kwargs):
        serializer: CreateOrderSerializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = OrderSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
