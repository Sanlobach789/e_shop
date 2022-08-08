from django.contrib import admin

from .models import Import, ImportItem, Shop


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
    list_display = ('name', 'quantity', 'created_at')
    inlines = (ImportItemInline,)
    search_fields = ('name',)
    ordering = ('-created_at',)

    @admin.display(description='Количество')
    def quantity(self, obj: Import):
        return obj.quantity

    def has_delete_permission(self, *args, **kwargs) -> bool:
        return False


admin.site.register(Shop)
