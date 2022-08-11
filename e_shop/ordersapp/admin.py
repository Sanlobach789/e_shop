from django.contrib import admin

from ordersapp.models import *


# TODO: сделать форму, где будет item - readonly и quantity будет иметь max-value.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at', 'status', 'finished_at')
    inlines = (OrderItemInline,)

    def get_readonly_fields(self, request, obj):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj is not None:
            readonly_fields.append('organization')
            readonly_fields.append('customer_data')
        return readonly_fields


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('title', 'inn', 'kpp')


@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'created_at', 'updated_at', 'finished_at', 'status')
