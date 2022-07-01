from django.contrib import admin
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from mainapp.models import Category, Item, Filter, ItemFilter, CategoryFilter
from mainapp.forms import CategoryForm


class CategoryFilterInline(admin.TabularInline):
    model = CategoryFilter
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image', 'parent_category']
    list_editable = ['title', 'image', 'parent_category']
    ordering = ['id']
    search_fields = ['title']
    form = CategoryForm
    inlines = [CategoryFilterInline]


class ItemFilterInline(admin.TabularInline):
    model = ItemFilter
    extra = 0
    readonly_fields = ['filter']
    fields = ['filter', 'name']
    # FIXME: не работает
    exclude = ['DELETE']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'category']
    # TODO: не показывать ItemFilterInline при создании,
    # но показывать при обновлении
    inlines = [ItemFilterInline]


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    prepopulated_fields = {'key': ('name', )}
    list_display = ['id', 'name', 'key']
    list_editable = ['name', 'key']
    ordering = ['id']


@receiver(pre_save, sender=CategoryFilter)
def add_item_filters_existing(instance: CategoryFilter, **kwargs):
    '''
    Добавление/обновление фильтров товаров ("синхронизация" с категориями)
    '''
    # Получаем старый прошлый фильтр категории.
    try:
        category_filter_old = CategoryFilter.objects\
                            .select_related('category', 'filter')\
                            .get(pk=instance.pk)
    except:
        category_filter_old = None

    # Если фильтр есть (его обновили)
    if category_filter_old:

        # Получаем фильтры (свойства) товаров
        item_filters = ItemFilter.objects.filter(
            filter=category_filter_old.filter,
            item__in=category_filter_old.category.item_set.all()
        )
        
        # Меняем фильтры товаров
        item_filters.update(filter=instance.filter, name='', value='')

    # Если фильтра у категории нет (добавили)
    else:
        
        # Получаем все товары из категории
        for item in instance.category.item_set.all():
        
            # Создаем пустой фильтр (свойство) для товара
            ItemFilter.objects.create(filter=instance.filter, item=item)


@receiver(post_save, sender=Item)
def add_item_filters_new_item(instance: Item, created: bool, **kwargs):
    '''
    Добавление фильтров категории к новому товарам
    '''
    if created:
        # Получаем фильтры категорий
        category_filters = instance.category.categoryfilter_set.select_related('filter')
        for cf in category_filters:
            # Добавляем фильтры товару
            ItemFilter.objects.create(item=instance, filter=cf.filter)

