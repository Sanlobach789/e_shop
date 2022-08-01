from django.contrib import admin

from .models import Basket, ItemBasket


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
    list_display = ('user',)
    readonly_fields = ('user',)
    inlines = (ItemBasketInline,)
