from django.contrib import admin

from .forms import (
    ItemPropertyForm, ItemForm, CategoryFilterValueForm, CategoryForm
)
from .models import (
    Category, Filter, CategoryFilter, Item, ItemProperty, CategoryFilterValue, ItemImage
)


class CategoryInline(admin.TabularInline):
    """Inline форма категорий"""
    model = Category
    extra = 0


class CategoryFilterInline(admin.TabularInline):
    """Inline форма фильтров категории"""
    model = CategoryFilter
    extra = 0


class ItemPropertyInline(admin.TabularInline):
    """Inline форма свойств (фильтров) товара"""
    model = ItemProperty
    extra = 0
    form = ItemPropertyForm
    can_delete = False
    readonly_fields = ('filter',)
    fields = ('filter', 'value')

    def has_add_permission(self, request, obj) -> bool:
        return False


class CategoryFilterValueInline(admin.TabularInline):
    """Inline форма значений фильтров"""
    model = CategoryFilterValue
    extra = 0
    exclude = ('value',)
    form = CategoryFilterValueForm


class ItemImageInline(admin.TabularInline):
    """Inline форма изображений товара"""
    model = ItemImage
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin форма для категорий"""
    list_display = ('name', 'image', 'parent_category', 'node')
    list_editable = ('image', 'parent_category', 'node')
    ordering = ('id',)
    search_fields = ('name',)
    form = CategoryForm

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id, None)
        if obj.node:
            self.inlines = [CategoryInline]
        else:
            self.inlines = [CategoryFilterInline]
        return super(CategoryAdmin, self).change_view(request, object_id, form_url='', extra_context=None)

    def add_view(self, request, form_url='', extra_context=None):
        self.inlines = []
        return super(CategoryAdmin, self).add_view(request, form_url='', extra_context=None)

    def get_field_queryset(self, db, db_field, request):
        if db_field.name == 'parent_category':
            return Category.get_node_categories()
        return super().get_field_queryset(db, db_field, request)


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    """Admin форма для фильтров"""
    list_display = ('name',)
    ordering = ('id',)
    search_fields = ('name',)
    prepopulated_fields = {'key': ('name',)}
    inlines = (CategoryFilterValueInline,)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Admin форма для товаров"""
    list_display = ('name', 'category', 'price', 'old_price',
                    'weight', 'quantity', 'basket_quantity')
    readonly_fields = ('basket_quantity',)
    ordering = ('id',)
    search_fields = ('name',)
    form = ItemForm

    @admin.display(description='В корзинах пользователей')
    def basket_quantity(self, obj: Item) -> int:
        return obj.basket_quantity

    def get_inlines(self, request, obj):
        inlines = [ItemImageInline]
        if obj:
            inlines.append(ItemPropertyInline)
        return inlines


@admin.register(CategoryFilterValue)
class CategoryFilterValueAdmin(admin.ModelAdmin):
    """Admin форма для значений фильтров"""
    list_display = ('filter', 'name', 'category')
    ordering = ('category', 'filter')
    prepopulated_fields = {'value': ('name',)}
    form = CategoryFilterValueForm
