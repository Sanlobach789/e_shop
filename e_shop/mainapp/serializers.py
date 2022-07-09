from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method

from mainapp.models import Category, CategoryFilter, CategoryFilterValue, Item


class FilterValueSerializer(serializers.ModelSerializer):
    """Сериализатор для значения фильтра"""
    class Meta:
        model = CategoryFilterValue
        fields = ('name', 'value')


class FilterSerializer(serializers.ModelSerializer):
    """Сериализатор для фильтра"""
    name = serializers.SerializerMethodField()
    key = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()

    class Meta:
        model = CategoryFilter
        fields = ('name', 'key', 'values')

    def get_name(self, obj: CategoryFilter):
        return obj.filter.name

    def get_key(self, obj: CategoryFilter):
        return obj.filter.key

    @swagger_serializer_method(FilterValueSerializer(many=True))
    def get_values(self, obj: CategoryFilter):
        values = CategoryFilterValue.objects.filter(category=obj.category, filter=obj.filter)
        return FilterValueSerializer(values, many=True).data


class SubCategorySerializer(serializers.ModelSerializer):
    """Сериализатор для подкатегории"""
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'node')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории"""
    sub_categories = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    filters = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'sub_categories', 'filters', 'node')

    @swagger_serializer_method(SubCategorySerializer(many=True))
    def get_sub_categories(self, obj: Category):
        sub_categories = obj.category_set.all()
        return SubCategorySerializer(sub_categories, many=True).data

    def get_image(self, obj: Category):
        return obj.image.url

    @swagger_serializer_method(FilterSerializer(many=True))
    def get_filters(self, obj: Category):
        filters = obj.categoryfilter_set.all()
        return FilterSerializer(filters, many=True).data


class ItemShortSerializer(serializers.ModelSerializer):
    """Сериализатор для краткой информации о товаре"""
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = ('id', 'name', 'price', 'old_price', 'images')

    @swagger_serializer_method(serializers.ListField(child=serializers.CharField()))
    def get_images(self, obj: Item):
        images = map(
            lambda x: x.image.url,
            obj.itemimage_set.all()
        )
        return images


class ItemPropertySerializer(serializers.Serializer):
    """Сериализатор для свойства (фильтра) товара"""
    name = serializers.CharField()
    value = serializers.CharField()


class ItemSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о товаре"""
    images = serializers.SerializerMethodField()
    properties = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = ('id', 'name', 'price', 'old_price', 'description', 'width',
                  'height', 'depth', 'weight', 'images', 'properties')

    @swagger_serializer_method(serializers.ListField(child=serializers.CharField()))
    def get_images(self, obj: Item):
        images = map(
            lambda x: x.image.url,
            obj.itemimage_set.all()
        )
        return images
    
    @swagger_serializer_method(ItemPropertySerializer(many=True))
    def get_properties(self, obj: Item):
        properties = [
            {
                'name': itemproperty.filter.name,
                'value': itemproperty.value.name
            }
            for itemproperty in obj.itemproperty_set.select_related('value', 'filter')
            if itemproperty.value
        ]
        return ItemPropertySerializer(properties, many=True).data
