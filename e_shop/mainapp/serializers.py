from rest_framework import serializers

from mainapp.models import Category

from django.db import connection


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'parent_category']

    def validate_parent_category(self, value):

        # Если родительская категория не равна null.
        if value:

            # Категория не может находится в самой себе.
            if self.instance.pk == value.pk:
                raise serializers.ValidationError('A category cannot be in itself.')
            
            # Проверка на цикличность категории.
            cursor = connection.cursor()
            # TODO: может SQL запросы вынести в какой-ниюудь файл?
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
            cursor.execute(query, (value.pk, self.instance.pk))
            
            result = cursor.fetchone()[0]
            if result != 0:
                raise serializers.ValidationError('The cyclicality of the categories was found.')

        return value

class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']
