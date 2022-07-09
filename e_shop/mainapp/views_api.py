from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from mainapp.models import Category, Item
from mainapp.serializers import CategorySerializer, ItemShortSerializer, ItemSerializer

from drf_yasg.utils import swagger_auto_schema


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
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ItemShortSerializer
        elif self.action == 'retrieve':
            return ItemSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        try:
            category = get_object_or_404(Category, pk=self.kwargs.get('category_id'))
            items = category.item_set.all()
        except:
            items = []
        return items
