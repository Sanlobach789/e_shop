from django.contrib import admin

from .forms import (
    ItemPropertyForm, ItemForm, CategoryFilterValueForm, CategoryForm
)
from .models import (
    Category, Filter, CategoryFilter, Item, ItemProperty, CategoryFilterValue
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
    
    def has_add_permission(self, request, obj) -> bool:
        return False


class CategoryFilterValueInline(admin.TabularInline):
    """Inline форма значений фильтров"""
    model = CategoryFilterValue
    extra = 0
    exclude = ('value',)
    form = CategoryFilterValueForm


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin форма для категорий"""
    list_display = ('name', 'image', 'parent_category', 'node')
    list_editable = ('image', 'parent_category', 'node')
    ordering = ('id',)
    search_fields = ('name',)
    form = CategoryForm

    # TODO: если node = True, показывать только категории, иначе - только фильтры
    def get_inlines(self, request, obj):
        inlines = [CategoryInline, CategoryFilterInline]
        # inlines = []
        # if obj:
        #     if not obj.node:
        #         inlines.append(CategoryFilterInline)
        #     else:
        #         inlines.append(CategoryInline)
        return inlines

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
    list_display = ('category',)
    ordering = ('id',)
    form = ItemForm

    def get_inlines(self, request, obj):
        inlines = []
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
