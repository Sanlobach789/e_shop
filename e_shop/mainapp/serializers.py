from rest_framework import serializers

from mainapp.models import Category

from drf_yasg.utils import swagger_serializer_method


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'image']


class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'sub_categories']

    @swagger_serializer_method(SubCategorySerializer(many=True))
    def get_sub_categories(self, obj: Category):
        sub_categories = Category.objects.filter(parent_category=obj.pk)
        return SubCategorySerializer(sub_categories, many=True).data

    def get_image(self, obj: Category):
        return obj.image.url
