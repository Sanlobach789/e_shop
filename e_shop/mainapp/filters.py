from django_filters import rest_framework as filters
from django.db.models import Q, Count

from .models import Item, ItemProperty


class ItemFilter(filters.FilterSet):
    """Фильтр для товаров"""
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_weight = filters.NumberFilter(field_name='weight', lookup_expr='gte')
    max_weight = filters.NumberFilter(field_name='weight', lookup_expr='lte')

    class Meta:
        model = Item
        fields = ('name',)

    def filter_queryset(self, queryset):
        # Кастомная фильтрация

        queryset = super().filter_queryset(queryset)
        
        if queryset:
            # Получаем категорию, в которой осуществляется фильтрация
            category = queryset[0].category
            
            # Получаем фильтры, которые находятся в запросе
            # NOTE: если фильтров нет в данной категории
            # и нужно искать по этим фильтрам, то нужно
            # вставить `CategoryFilter` вместо `category.categoryfilter_set`
            filters = list(map(
                lambda x: x.filter,
                category.categoryfilter_set
                    .filter(filter__key__in=self.data)
                    .select_related('filter')
            ))
            filters_count = len(list(filters))
            
            if filters_count > 0:
                condition = Q()
                for filter in filters:
                    sub_condition = Q()
                    for value in self.data.getlist(filter.key):
                        if not value:
                            continue
                        sub_condition |= Q(value__value=value)
                    condition |= Q(value__filter=filter) & sub_condition
                condition = (Q(value__category=category) | Q(value__category=None)) & condition
                
                # Список id товаров, которые удовлетворяют условиям
                satisfy_item_id_list = map(
                    lambda x: x['item'],
                    ItemProperty.objects
                        .filter(condition)
                        .values('item')
                        .annotate(count=Count('item'))
                        .filter(count=filters_count)
                )

                # Получение товаров, которые удовлетворяют условиям
                queryset = queryset.filter(pk__in=satisfy_item_id_list)

        return queryset
