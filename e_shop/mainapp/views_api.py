from django.http import Http404
from rest_framework import viewsets
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404

from .models import Category, Item
from .filters import ItemFilter
from .serializers import CategorySerializer, ItemShortSerializer, ItemSerializer


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(responses={
        404: 'Category Not Found'
    })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ItemModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    filterset_class = ItemFilter
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ItemShortSerializer
        elif self.action == 'retrieve':
            return ItemSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        try:
            category = get_object_or_404(Category, pk=self.kwargs.get('category_id'))
            items = category.item_set
        except Http404 as e:
            category = None
            items = Item.objects

        return items.all()
