from http import HTTPStatus

from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema

from .models import Delivery, Order, Organization
from .serializers import (
    CreateOrderSerializer, DeliverySerializer, OrderSerializer, OrganizationSerializer,
    ActionStatusOrderSerializer, StatusOrderSerializer
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

    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: StatusOrderSerializer,
        HTTPStatus.BAD_REQUEST: 'Bad Request',
        HTTPStatus.NOT_FOUND: 'Not Found',
    }, serializer_class={})
    @action(methods=['POST'], detail=True, serializer_class=ActionStatusOrderSerializer)
    def finish(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        order.finish()
        return Response(StatusOrderSerializer(order).data)


class OrganizationModelViewSet(viewsets.GenericViewSet,
                               mixins.CreateModelMixin):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class DeliveryModelViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
