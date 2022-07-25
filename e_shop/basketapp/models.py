from decimal import Decimal
from typing import Union, List, Tuple

from django.db import models, transaction
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404

from mainapp.models import Item


class Basket(models.Model):
    """Модель корзины"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                verbose_name='Пользователь')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self) -> str:
        return f'Корзина {self.user.email}'

    def add_item(self, item: Union[Item, int], quantity: int = 1) -> 'ItemBasket':
        """Добавить товар в корзину"""
        if quantity < 0:
            raise ValueError('Нельзя добавить отрицательное колчество товаров')
        if isinstance(item, int):
            item = get_object_or_404(Item, pk=item)

        itembasket, _ = self.itembasket_set.get_or_create(item=item)
        itembasket.quantity += quantity
        itembasket.save()
        return itembasket

    def remove_item(self, item: Item, quantity: int = 1, remove_all: bool = False) -> None:
        """Убрать товар из корзины"""
        if quantity < 0:
            raise ValueError('Нельзя убрать отрицательное колчество товаров')
        if isinstance(item, int):
            item = get_object_or_404(Item, pk=item)

        itembasket = self.itembasket_set.get(item=item)
        if remove_all:
            itembasket.quantity -= itembasket.quantity
        else:
            itembasket.quantity -= min(itembasket.quantity, quantity)

        itembasket.save()

    def sync(self, items: List[Tuple[Union[Item, int], int]]) -> None:
        """Синхронизирует корзину"""
        items_basket = self.itembasket_set.select_related('item').all()
        with transaction.atomic():
            for item, quantity in items:
                item_basket = items_basket.filter(**(
                    {'item_id': item} if isinstance(item, int) else {'item': item}
                )).first()

                if not item_basket:
                    self.add_item(item, quantity)
                else:
                    add_quantity = quantity - item_basket.quantity
                    if add_quantity > 0:
                        self.add_item(item_basket.item, add_quantity)

    def clear(self) -> None:
        """Очищает корзину"""
        self.itembasket_set.all().delete()

    @property
    def quantity(self) -> int:
        return self.itembasket_set.aggregate(quantity=models.Sum('quantity'))['quantity']

    @property
    def store_quantity(self) -> int:
        return self.itembasket_set.aggregate(quantity=models.Sum(
            models.Min(models.F('quantity'), models.F('item__quantity'))))['quantity']

    @property
    def cost(self) -> Decimal:
        return self.itembasket_set.aggregate(cost=models.Sum(
            models.Min(models.F('quantity'), models.F('item__quantity'))
            * models.F('item__price')))['cost']


class ItemBasket(models.Model):
    """Модель товара в корзине"""
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE,
                               verbose_name='Корзина')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,
                             verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество', default=0)

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзинах'
        unique_together = ('basket', 'item')


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_basket_for_user_on_create(instance: settings.AUTH_USER_MODEL, created: bool, **kwargs):
    """
    Создает корзину для нового пользователя
    """
    if created:
        Basket.objects.create(user=instance)


@receiver(post_save, sender=ItemBasket)
def delete_item_from_basket(instance: ItemBasket, **kwargs):
    """
    Удаляет полностью товар из корзины, если его количество в корзине равно 0
    """
    if instance.quantity == 0:
        instance.delete()
