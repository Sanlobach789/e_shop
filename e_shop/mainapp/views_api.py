from rest_framework import viewsets

from mainapp.models import Category
from mainapp.serializers import CategorySerializer


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
