# from rest_framework import serializers

# from mainapp.models import Category, Filter, ItemFilter

# from drf_yasg.utils import swagger_serializer_method


# class FilterValueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ItemFilter
#         fields = ['name', 'value']


# class FilterSerializer(serializers.ModelSerializer):
#     values = serializers.SerializerMethodField()

#     class Meta:
#         model = Filter
#         fields = ['key', 'name', 'values']

#     @swagger_serializer_method(FilterValueSerializer(many=True))
#     def get_values(self, obj: Filter):
#         values = obj.itemfilter_set.all()
#         return FilterValueSerializer(values, many=True).data


# class SubCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'title', 'image']


# class CategorySerializer(serializers.ModelSerializer):
#     sub_categories = serializers.SerializerMethodField()
#     image = serializers.SerializerMethodField()
#     filters = serializers.SerializerMethodField()

#     class Meta:
#         model = Category
#         fields = ['id', 'title', 'image', 'sub_categories', 'filters']

#     @swagger_serializer_method(SubCategorySerializer(many=True))
#     def get_sub_categories(self, obj: Category):
#         sub_categories = obj.category_set.all()
#         return SubCategorySerializer(sub_categories, many=True).data

#     def get_image(self, obj: Category):
#         return obj.image.url

#     @swagger_serializer_method(FilterSerializer(many=True))
#     def get_filters(self, obj: Category):
#         filters = [
#             category_filter.filter
#             for category_filter in (
#                 obj.categoryfilter_set
#                 .prefetch_related('filter__itemfilter_set')
#             )
#         ]
#         return FilterSerializer(filters, many=True).data

#     def select_sub_categories(self, pk):
#         return Category.objects.filter(parent_category=pk)
