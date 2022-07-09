import os
from uuid import uuid4

from django.db import models, connection
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save, post_delete


def path_and_rename(instance, filename):
    upload_to = MODEL_STORAGE_DIRECTORIES[type(instance)]
    ext = filename.split('.')[-1]
    # get filename from uuid pk
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Filter(models.Model):
    """Модель фильтра"""
    name = models.CharField('Название', max_length=256)
    key = models.SlugField('Ключ поиска', unique=True, db_index=True, blank=True)

    class Meta:
        verbose_name = 'Фильтр'
        verbose_name_plural = 'Фильтры'

    def __str__(self) -> str:
        return f'{self.name}'

    def save(self, *args, **kwargs) -> None:
        self.key = slugify(self.name, allow_unicode=True)
        return super().save(*args, **kwargs)


class Category(models.Model):
    """Модель категории"""
    name = models.CharField('Название', max_length=256)
    image = models.ImageField('Картинка', upload_to=path_and_rename,
                              blank=True, default='no-avatar.jpg')
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name='Родительский каталог')
    node = models.BooleanField('Узловая', default=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return f'{self.name} ({self.id})'

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        # Валидация данных модели

        # region Валидация parent_category.
        if self.parent_category:

            # Категория не может находится в самой себе.
            if self.pk == self.parent_category.pk:
                raise ValidationError('A category cannot be in itself.')
            
            # Проверка на цикличность категории.
            cursor = connection.cursor()
            # NOTE: может SQL запросы вынести в какой-ниюудь файл?
            query = '''
            WITH RECURSIVE tmp AS (
                SELECT fc.id, fc.parent_category_id
                FROM mainapp_category AS fc
                WHERE fc.id = %s

                UNION ALL

                SELECT sc.id, sc.parent_category_id
                FROM mainapp_category sc
                JOIN tmp
                ON sc.id = tmp.parent_category_id
            )
            SELECT COUNT(tmp.id)
            FROM tmp
            WHERE tmp.id = %s;
            '''
            cursor.execute(query, (self.parent_category.pk, self.pk))
            
            result = cursor.fetchone()[0]
            if result != 0:
                raise ValidationError('The cyclicality of the categories was found.')
        
        # endregion
        
        # region Проверка node
        # Узловая категория не может содержать товаров
        if self.node and self.item_set.count() > 0:
            raise ValidationError('The node cannot contain products.')
        
        # Не узловая категория не может содержать подкатегорий
        if not self.node and self.category_set.count() > 0\
            or self.parent_category and not self.parent_category.node:
            raise ValidationError('The non-node cannot contain subcategories.')
        # endregion
        
        return super().clean()

    @staticmethod
    def get_non_node_categories():
        """
        Получить категории, которые не являются узлами
        """
        return Category.objects.filter(node=False)

    @staticmethod
    def get_node_categories():
        """
        Получить категории, которые являются узлами
        """
        return Category.objects.filter(node=True)


class CategoryFilter(models.Model):
    """Модель для связи фильтров с категориями"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE, verbose_name='Фильтр')

    class Meta:
        verbose_name = 'Фильтр категрии'
        verbose_name_plural = 'Фильтры категории'
        unique_together = ('category', 'filter')

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        # Валидация данных модели
        
        # Узловая категория не может иметь фильтров
        if self.category.node:
            raise ValidationError('A node category cannot have filters.')
        
        return super().clean()


class Item(models.Model):
    """Модель товара"""
    name = models.CharField('Название', max_length=256)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=2, null=True, blank=False)
    description = models.CharField('Описание', max_length=256)
    width = models.PositiveIntegerField('Ширина')
    height = models.PositiveIntegerField('Высота')
    depth = models.PositiveIntegerField('Толщина')
    weight = models.PositiveIntegerField('Вес')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class ItemImage(models.Model):
    """Модель изображения товара"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    image = models.ImageField('Изображение', upload_to=path_and_rename,
                              blank=True, default='no-avatar.jpg')
    priority = models.SmallIntegerField('Приоритет')

    class Meta:
        ordering = ('priority',)
    

class CategoryFilterValue(models.Model):
    """Модель значения фильтра в категории"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE, verbose_name='Фильтр')
    name = models.CharField('Название', max_length=256)
    value = models.SlugField('Значение', db_index=True)

    class Meta:
        verbose_name = 'Значение фильтра'
        verbose_name_plural = 'Значения фильтров'
        unique_together = ('category', 'filter', 'value')

    def __str__(self) -> str:
        return f'{self.name}'

    def save(self, *args, **kwargs) -> None:
        self.value = slugify(self.name, allow_unicode=True)
        return super().save(*args, **kwargs)


class ItemProperty(models.Model):
    """Модель совойства (фильтра) товара"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE, verbose_name='Фильтр')
    value = models.ForeignKey(CategoryFilterValue, on_delete=models.CASCADE,
                              null=True, blank=True, verbose_name='Свойство')

    class Meta:
        unique_together = ('item', 'filter')


MODEL_STORAGE_DIRECTORIES = {
    Category: 'category_images',
    ItemImage: 'item_images',
}


@receiver(post_save, sender=Item)
def add_item_property_on_create(instance: Item, created: bool, **kwargs):
    """
    Добаляет к новому товару свойства (фильтры) категории
    """
    if created:
        category_filters = instance.category.categoryfilter_set.select_related('filter')
        new_filters_for_item = map(lambda x: ItemProperty(item=instance, filter=x.filter),
                                   category_filters)
        ItemProperty.objects.bulk_create(new_filters_for_item)


@receiver(pre_save, sender=Item)
def change_item_property_on_move(instance: Item, **kwargs):
    """
    Добавляет/удаляет свойства (фильтры) товара при перемещении его в другую категорию
    """
    # Пробуем получить товар из бд
    try:
        old_item = Item.objects.select_related('category').get(pk=instance.pk)
    except:
        old_item = None

    # Если он есть (значит мы обновляем его, иначе - создаем)
    if old_item:
        # Если товар был перемещен
        if old_item.category != instance.category:
            # Удаляем свойства (фильтры) из товара, которых нет в новой категории
            instance.itemproperty_set.exclude(
                filter__in=map(
                    lambda x: x.filter,
                    instance.category.categoryfilter_set.select_related('filter'))
            ).delete()
            # Сбрасываем значение свойства (фильтра) товара, которые есть в обеих категориях
            instance.itemproperty_set.update(value=None)
            # Добавляем новые свойства (фильтры) новой категории товару
            ItemProperty.objects.bulk_create(map(
                lambda x: ItemProperty(item=instance, filter=x.filter),
                instance.category.categoryfilter_set.select_related('filter').exclude(filter__in=map(
                    lambda x: x.filter,
                    instance.itemproperty_set.select_related('filter')
                ))
            ))


@receiver(post_save, sender=CategoryFilter)
def add_item_property_on_filter_create(instance: CategoryFilter, created: bool, **kwargs):
    """
    Добавляет фильтр (свойство), который был добавлен к категории, товарам в этой категории
    """
    if created:
        ItemProperty.objects.bulk_create(map(
            lambda x: ItemProperty(item=x, filter=instance.filter),
            instance.category.item_set.exclude(pk__in=map(          # получаем товары категории,
                lambda y: y.item.pk,                                # к которой добавлен фильтр,
                ItemProperty.objects.filter(filter=instance.filter) # учитывая, что товары с таким
                                    .select_related('item')         # фильтром уже есть.
            ))
        ))


@receiver(post_delete, sender=CategoryFilter)
def delete_item_property_on_filter_remove(instance: CategoryFilter, **kwargs):
    """
    Удаляет фильтр (свойство), из товаров, когда он был удален из категории
    """
    ItemProperty.objects.filter(item__in=instance.category.item_set.all(), filter=instance.filter).delete()
