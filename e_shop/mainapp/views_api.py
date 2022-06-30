from rest_framework import viewsets

from mainapp.models import Category
from mainapp.serializers import CategorySerializer

from drf_yasg.utils import swagger_auto_schema


class CategoryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @swagger_auto_schema(responses={
        404: 'Category Not Found'
    })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
