from django.contrib import admin
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete

from mainapp.forms import CategoryForm
from mainapp.models import Category, Item, Filter, ItemFilter, CategoryFilter


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
    can_delete = False


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'category']
    
    def get_inlines(self, obj, *args, **kwargs):
        # Если товар уже создан
        if obj:
            # Показываем фильтры
            return [ItemFilterInline]
        # Если товар только создается
        else:
            # Скрываем фильтры
            return []


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


@receiver(post_delete, sender=CategoryFilter)
def remove_item_filters_on_delete_category_filter(instance: CategoryFilter, **kwargs):
    '''
    Удаляет фильтры из товаров,
    которые были удалены из категории
    '''
    # Получаем товары в категории
    items = instance.category.item_set.all()
    # Удаляем фильтр из товаров категории
    ItemFilter.objects.filter(filter=instance.filter, item__in=items).delete()


@receiver(post_save, sender=Item)
def add_item_filters_new_item(instance: Item, created: bool, **kwargs):
    '''
    Добавление фильтров категории к новому товарам
    '''
    # Получаем фильтры категории
    category_filters = instance.category.categoryfilter_set.select_related('filter')
        
    # Если создаем товар
    if created:
        for cf in category_filters:
            # Добавляем фильтры товару
            ItemFilter.objects.create(item=instance, filter=cf.filter)

    # NOTE: вынести в pre_save, чтобы проверить,
    # поменялся ли родитель. Если нет, то не надо
    # выполнять этот блок кода.
    # Если меняем что-то в товаре
    else:
        # Удаляем из товара фильтры, которых нет в новой категории
        instance.itemfilter_set.exclude(filter__in=category_filters.values_list('filter')).delete()
        
        # Добавляем в товар фильтры, которые есть
        # в новой категории, но нет в товаре
        for cf in category_filters.exclude(filter__in=instance.itemfilter_set.values_list('filter')):
            # Добавляем фильтры товару
            ItemFilter.objects.create(item=instance, filter=cf.filter)
