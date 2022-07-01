import os
from uuid import uuid4

from django.db import models, connection
from django.utils.text import slugify
from django.core.exceptions import ValidationError


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


# Фильтр
class Filter(models.Model):
    name = models.CharField(max_length=256)                         # название фильтра
    key = models.SlugField(unique=True, db_index=True, blank=True)  # ключ (идетификатор фильтра)

    def save(self, *args, **kwargs) -> None:
        self.key = slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


# Категория
class Category(models.Model):
    title = models.CharField(max_length=256, )
    image = models.ImageField(upload_to=path_and_rename, blank=True, default="no-avatar.jpg")
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def clean(self) -> None:
        # Валидация данных модели.

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
            
        return super().clean()

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f'{self.title} ({self.id})'


# Товар
class Item(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


# Модель для связи фильтров с товарами
class ItemFilter(models.Model):
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    name = models.CharField(max_length=256) # название значения
    value = models.SlugField(db_index=True) # значение для фильтрации

    class Meta:
        unique_together = ('item', 'filter')

    def save(self, *args, **kwargs) -> None:
        self.value = slugify(self.name)
        return super().save(*args, **kwargs)


# Модель для связи фильтров с категориями
class CategoryFilter(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('category', 'filter')


MODEL_STORAGE_DIRECTORIES = {
    Category: 'categories_images'
}
