from rest_framework import serializers

from mainapp.models import Category, Filter

from drf_yasg.utils import swagger_serializer_method


class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ['key', 'name', 'values']


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image']


class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    filters = FilterSerializer(many=True)

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'sub_categories', 'filters']

    @swagger_serializer_method(SubCategorySerializer(many=True))
    def get_sub_categories(self, obj: Category):
        sub_categories = obj.category_set.all()
        return SubCategorySerializer(sub_categories, many=True).data

    def get_image(self, obj: Category):
        return obj.image.url

    def select_sub_categories(self, pk):
        return Category.objects.filter(parent_category=pk)
