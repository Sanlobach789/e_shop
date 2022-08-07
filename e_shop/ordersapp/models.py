from uuid import uuid4

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from authapp.models import User
from basketapp.models import Basket


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=256, verbose_name="Название")
    inn = models.CharField(max_length=50, verbose_name="ИНН")
    kpp = models.CharField(max_length=50, verbose_name="КПП")


class CustomerData(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = PhoneNumberField(null=False, blank=True)
    email = models.EmailField()


class Order(models.Model):
    CREATED = "CRE"
    IN_PROGRESS = "INP"
    WAITING_FOR_PICKUP = "WFP"
    WAITING_FOR_PAYMENT = "WPA"
    PAID = "PAY"
    DELIVERY = "DEL"
    FINISHED = "FIN"
    STATUS_CHOICES = [
        (CREATED, "Создан"),
        (IN_PROGRESS, "Находится в обработке"),
        (WAITING_FOR_PICKUP, "Готов к выдаче"),
        (WAITING_FOR_PAYMENT, "Ожидает оплату"),
        (PAID, "Оплачен"),
        (DELIVERY, "В доставке"),
        (FINISHED, "Завершен"),
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    finished_at = models.DateTimeField(verbose_name="Дата завершения")
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=CREATED, verbose_name="Статус")
    basket = models.ForeignKey(Basket, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Корзина")
    customer_data = models.ForeignKey(CustomerData, on_delete=models.SET_NULL, null=True, verbose_name="Контактное лицо")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заказу")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True)

