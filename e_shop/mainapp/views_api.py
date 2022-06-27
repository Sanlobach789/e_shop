from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mainapp.models import Category
from mainapp.serializers import CategorySerializer, CategoryChildSerializer


class CategoryModelViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=True, methods=['GET'])
    def childs(self, request, pk=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        category_serializer = self.get_serializer(category)
        
        childs = self.get_queryset().filter(parent_category=category.pk)
        childs_serializer = CategoryChildSerializer(childs, many=True)
        
        return Response(dict(
            category=category_serializer.data,
            childs=childs_serializer.data
        ))
