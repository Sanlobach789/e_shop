from http import HTTPStatus

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from .models import Basket
from .serializers import (
    BasketSerializer, ItemBasketActionSerializer, ManyItemBasketActionSerializer
)

class BasketModelViewSet(viewsets.GenericViewSet):
    basket: Basket
    serializer_class = BasketSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Basket.objects.none()

    def initial(self, request, *args, **kwargs):
        self.basket = request.user.basket
        return super().initial(request, *args, **kwargs)

    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: 'Ok',
        HTTPStatus.UNAUTHORIZED.value: 'Unauthorized',
    })
    def list(self, request):
        return Response(BasketSerializer(self.basket).data)

    @action(methods=['POST'], detail=False, serializer_class=ItemBasketActionSerializer)
    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: 'Ok',
        HTTPStatus.BAD_REQUEST.value: 'Invalid Body',
        HTTPStatus.NOT_FOUND.value: 'Item Not Found',
        HTTPStatus.UNAUTHORIZED.value: 'Unauthorized',
    })
    def add(self, request):
        """Добавляет товар к корзине"""
        serializer = ItemBasketActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        self.basket.add_item(item=data['item_id'], quantity=data['quantity'])
        return Response(status=HTTPStatus.OK.value)

    @action(methods=['POST'], detail=False, serializer_class=ItemBasketActionSerializer)
    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: 'Ok',
        HTTPStatus.BAD_REQUEST.value: 'Invalid Body',
        HTTPStatus.UNAUTHORIZED.value: 'Unauthorized',
        HTTPStatus.NOT_FOUND.value: 'Item Not Found',
    })
    def remove(self, request):
        """Убирает товар из корзины"""
        serializer = ItemBasketActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        self.basket.remove_item(item=data['item_id'], quantity=data['quantity'])
        return Response(status=HTTPStatus.OK.value)

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: 'Ok',
        HTTPStatus.UNAUTHORIZED.value: 'Unauthorized',
    })
    def clear(self, request):
        """Очищает корзину"""
        self.basket.clear()
        return Response(status=HTTPStatus.OK.value)

    @action(methods=['POST'], detail=False, serializer_class=ManyItemBasketActionSerializer)
    @swagger_auto_schema(responses={
        HTTPStatus.OK.value: 'Ok',
        HTTPStatus.BAD_REQUEST.value: 'Invalid Body',
        HTTPStatus.UNAUTHORIZED.value: 'Unauthorized',
        HTTPStatus.NOT_FOUND.value: 'Item Not Found',
    })
    def sync(self, request):
        """Синхронизирует корзину"""
        items = ManyItemBasketActionSerializer(data=request.data)
        items.is_valid(raise_exception=True)
        self.basket.sync([(el['item_id'], el['quantity'])
                          for el in items.validated_data['items']])
        return Response(status=HTTPStatus.OK.value)
