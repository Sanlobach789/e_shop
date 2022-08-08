from django.contrib import admin

from ordersapp.models import *


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'updated_at', 'status', 'basket', 'finished_at')
    readonly_fields = ('organization', 'customer_data', 'basket', 'delivery')


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('title', 'inn', 'kpp')


@admin.register(CustomerData)
class CustomerDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'address', 'created_at', 'updated_at', 'finished_at', 'status')
