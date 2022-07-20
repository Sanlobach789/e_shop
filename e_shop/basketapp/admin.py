from django.contrib import admin

from .models import Basket, ItemBasket, Import, ImportItem


class ItemBasketInline(admin.TabularInline):
    """Inline форма товаров в корзине"""
    model = ItemBasket
    extra = 0
    readonly_fields = ('store_quantity',)

    @admin.display(description='В наличии')
    def store_quantity(self, obj: ItemBasket):
        return obj.item.quantity


@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    """Админ форма для корзины"""
    list_display = ('user', 'quantity', 'store_quantity', 'cost')
    readonly_fields = ('user',)
    inlines = (ItemBasketInline,)

    @admin.display(description='В корзине')
    def quantity(self, obj: Basket):
        return obj.quantity

    @admin.display(description='Доступно')
    def store_quantity(self, obj: Basket):
        return obj.store_quantity

    @admin.display(description='Стоимость')
    def cost(self, obj: Basket):
        return obj.cost


class ImportItemInline(admin.TabularInline):
    """Inline форма для элемента импорта"""
    model = ImportItem
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj: ImportItem) -> bool:
        is_create = obj is None
        return is_create

    def has_change_permission(self, request, obj: ImportItem) -> bool:
        is_create = obj is None
        return is_create


@admin.register(Import)
class ImportAdmin(admin.ModelAdmin):
    """Админ форма для импорта"""
    list_display = ('name', 'quantity')
    inlines = (ImportItemInline,)
    search_fields = ('name',)

    @admin.display(description='Количество')
    def quantity(self, obj: Import):
        return obj.quantity
