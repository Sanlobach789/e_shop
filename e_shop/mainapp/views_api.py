from django.http import Http404
from rest_framework import viewsets, filters, generics
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from .models import Category, Item
from .filters import ItemFilter, CustomPagination
from .serializers import CategorySerializer, ItemShortSerializer, ItemSerializer


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.prefetch_related('categoryfiltervalue_set').all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(responses={
        404: 'Category Not Found'
    })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ItemModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    filterset_class = ItemFilter
    pagination_class = CustomPagination
    permission_classes = [AllowAny]

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

        items = items.prefetch_related('itemimage_set')
        return items.all()

    def filter_queryset(self, queryset):
        queryset = super(ItemModelViewSet, self).filter_queryset(queryset)
        if self.request.query_params.get("sort", None):
            return queryset.order_by(self.request.query_params.get("sort", None))
        else:
            return queryset


class SearchItemModelViewSet(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemShortSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
