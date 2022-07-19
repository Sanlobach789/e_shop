from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

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


class ItemBasket(models.Model):
    """Модель товара в корзине"""
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE,
                               verbose_name='Корзина')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,
                             verbose_name='Товар')
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзинах'
        unique_together = ('basket', 'item')


class Import(models.Model):
    """Модель импорта товаров"""
    name = models.CharField('Наименование', max_length=256)

    class Meta:
        verbose_name = 'Импорт'
        verbose_name_plural = 'Импорты'

    def __str__(self) -> str:
        return f'{self.name}'


class ImportItem(models.Model):
    """Модель элемента импорта"""
    import_obj = models.ForeignKey(Import, on_delete=models.CASCADE,
                                   verbose_name='Импорт')
    item = models.ForeignKey(Item, on_delete=models.CASCADE,
                             verbose_name='Товар')
    quantity = models.IntegerField('Количество')

    class Meta:
        unique_together = ('import_obj', 'item')

    def save(self, *args, **kwargs):
        self.item.quantity += self.quantity
        self.item.save()
        return super().save(*args, **kwargs)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_basket_for_user_on_create(instance: settings.AUTH_USER_MODEL, created: bool, **kwargs):
    """
    Создает корзину для нового пользователя
    """
    if created:
        Basket.objects.create(user=instance)
