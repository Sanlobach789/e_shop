from django.contrib import admin

from mainapp.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'image', 'parent_category']
    list_editable = ['title', 'image', 'parent_category']
    ordering = ['id']
    search_fields = ['title']
