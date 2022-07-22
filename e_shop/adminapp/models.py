from django.db import models

from mainapp.models import Item


class ImportItem(models.Model):
    """Модель элемента импорта"""
    import_obj = models.ForeignKey('Import', on_delete=models.CASCADE,
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


class Import(models.Model):
    """Модель импорта товаров"""
    name = models.CharField('Наименование', max_length=256)
    comment = models.TextField('Комментарий', default='', blank=True)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Импорт'
        verbose_name_plural = 'Импорты'

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def quantity(self) -> int:
        return self.importitem_set.aggregate(quantity=models.Sum('quantity'))['quantity']

    @staticmethod
    def import_from_item_form(item: Item, quantity: int) -> 'Import':
        """Создает импорт для товара при увеличения количества в форме товара"""
        action = 'Добавлено' if quantity >= 0 else 'Удалено'
        name = f'{item.name} | {action} | {abs(quantity)}'
        import_obj = Import.objects.create(name=name,
                                           comment='Этот импорт был сгенерирова автоматически')
        import_obj.importitem_set.create(import_obj=import_obj, item=item, quantity=quantity)
        return import_obj
