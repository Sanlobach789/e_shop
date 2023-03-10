from uuid import uuid4

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField

from adminapp.models import Shop
from authapp.models import User
from mainapp.models import Item

inn_validator = RegexValidator(r"[0-9]{12}", message="Некорректный ИНН.")
kpp_validator = RegexValidator(r"[0-9]{9}", message="Некорректный КПП.")


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=256, verbose_name="Название")
    inn = models.CharField(max_length=50, verbose_name="ИНН", validators=[inn_validator])
    kpp = models.CharField(max_length=50, verbose_name="КПП", validators=[kpp_validator])

    def __str__(self):
        return f'{self.title}, ИНН {self.inn}, КПП {self.kpp}'


class CustomerData(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=128, verbose_name="Имя")
    phone_number = PhoneNumberField(null=False, blank=True, verbose_name="Номер телефона")
    email = models.EmailField()

    def __str__(self):
        return f'{self.name}, {self.phone_number}, {self.email}'


class Delivery(models.Model):
    WAITING = "WA"
    COURIER = "CO"
    DELIVERED = "DE"
    STATUS_CHOICES = [
        (WAITING, "В ожидании"),
        (COURIER, "У курьера"),
        (DELIVERED, "Доставлено"),
    ]
    address = models.TextField(verbose_name="Адрес доставки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default=WAITING, verbose_name="Статус доставки")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий")

    def __str__(self):
        return f'{self.address} - {self.get_status_display()}'


class Order(models.Model):
    CREATED = "CRE"
    IN_PROGRESS = "INP"
    WAITING_FOR_PICKUP = "WFP"
    WAITING_FOR_PAYMENT = "WPA"
    PAID = "PAY"
    DELIVERY = "DEL"
    FINISHED = "FIN"
    CANCEL = "CAN"
    STATUS_CHOICES = [
        (CREATED, "Создан"),
        (IN_PROGRESS, "Находится в обработке"),
        (WAITING_FOR_PAYMENT, "Ожидает оплату"),
        (PAID, "Оплачен"),
        (WAITING_FOR_PICKUP, "Готов к выдаче"),
        (DELIVERY, "В доставке"),
        (FINISHED, "Завершен"),
        (CANCEL, "Отменен"),
    ]
    UPON_RECEIPT = "UR"
    TRANSFER = "TR"
    ONLINE = "ON"
    PAYMENT_CHOICES = [
        (UPON_RECEIPT, "При получении"),
        (TRANSFER, "Переводом"),
        (ONLINE, "Онлайн"),
    ]
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата завершения")
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default=CREATED, verbose_name="Статус")
    customer_data = models.ForeignKey(CustomerData, on_delete=models.SET_NULL, null=True, blank=True,
                                      verbose_name="Контактное лицо")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заказу")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name="Организация")
    pickup_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Самовывоз")
    payment_type = models.CharField(max_length=3, choices=PAYMENT_CHOICES, default=UPON_RECEIPT,
                                    verbose_name="Способ оплаты")
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Доставка")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveSmallIntegerField("Количество")
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, blank=True)
