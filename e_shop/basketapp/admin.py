from django.contrib import admin
from django.db.models import F, Sum, Min

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
    inlines = (ItemBasketInline,)

    @admin.display(description='В корзине')
    def quantity(self, obj: Basket):
        return obj.itembasket_set.aggregate(quantity=Sum('quantity'))['quantity']

    @admin.display(description='Доступно')
    def store_quantity(self, obj: Basket):
        return obj.itembasket_set.aggregate(quantity=Sum(Min(F('quantity'),
                                                             F('item__quantity'))))['quantity']

    @admin.display(description='Стоимость')
    def cost(self, obj: Basket):
        # TODO: решить нужно ли это, и если нужно, то в каком виде
        # Стомость корзины с учетом наличия
        return obj.itembasket_set.aggregate(cost=Sum(
            Min(
                F('quantity'), F('item__quantity')
            )
            * F('item__price')
        ))['cost']
        # Стоимость корзины без учета наличия
        # return obj.itembasket_set.aggregate(cost=Sum(F('quantity') * F('item__price')))['cost']


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

    @admin.display(description='Количество')
    def quantity(self, obj: Import):
        return obj.importitem_set.all().aggregate(quantity=Sum('quantity'))['quantity']
