from django.db import models

from mainapp.models import Item


class Import(models.Model):
    """Модель импорта товаров"""
    name = models.CharField('Наименование', max_length=256)

    class Meta:
        verbose_name = 'Импорт'
        verbose_name_plural = 'Импорты'

    def __str__(self) -> str:
        return f'{self.name}'

    @property
    def quantity(self) -> int:
        return self.importitem_set.aggregate(quantity=models.Sum('quantity'))['quantity']


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
