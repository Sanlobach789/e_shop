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
    customer_data = models.ForeignKey(CustomerData, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Контактное лицо")
    comment = models.TextField(null=True, blank=True, verbose_name="Комментарий к заказу")
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Организация")
    pickup_shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Самовывоз")
    payment_type = models.CharField(max_length=3, choices=PAYMENT_CHOICES, default=UPON_RECEIPT, verbose_name="Способ оплаты")
    delivery = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Доставка")

    __db_order: "Order" = None
    @property
    def db_order(self):
        if not self.__db_order:
            self.__db_order = Order.objects.get(pk=self.pk)
        return self.__db_order

    def save(self, *args, **kwargs) -> None:
        self.full_clean()

        if not self._state.adding:
            if self.delivery and self.pickup_shop:
                if self.db_order.delivery:
                    self.delivery = None
                elif self.db_order.pickup_shop:
                    self.pickup_shop = None
        return super().save(*args, **kwargs)

    def clean(self) -> None:
        if (
            self._state.adding and self.delivery and self.pickup_shop
            or not self.delivery and not self.pickup_shop
            ):
            raise ValidationError("Выберите один способ получения.")

        # Статусы заказов
        if self.db_order.status == self.FINISHED:
            raise ValidationError("Заказ уже выдан.")
        elif self.db_order.status == self.CANCEL:
            raise ValidationError("Заказ отменен.")

        return super().clean()

    def finish(self):
        """
        Подтверждает получение заказа.
        """
        self.status = self.FINISHED
        self.save()

    def cancel(self):
        """
        Отменяет заказ.
        """
        self.status = self.CANCEL
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveSmallIntegerField("Количество")
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2, blank=True)

    __db_orderitem: "OrderItem" = None
    @property
    def db_orderitem(self):
        if not self.__db_orderitem:
            self.__db_orderitem = OrderItem.objects.get(pk=self.pk)
        return self.__db_orderitem

    def save(self, *args, **kwargs) -> None:
        self.full_clean()

        if self.pk is None:
            self.change_quantity(self.quantity)

            # Автоматическая установка цены товара в заказе, если пользователь не указал.
            if self.price is None:
                self.price = self.item.price
        else:
            db_orderitem = self.db_orderitem
            if db_orderitem.quantity != self.quantity:
                self.change_quantity(self.quantity - db_orderitem.quantity)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.change_quantity(-self.db_orderitem.quantity)
        return super().delete(*args, **kwargs)

    def clean(self) -> None:
        if self.pk is not None:
            db_orderitem = self.db_orderitem
            if db_orderitem.item != self.item:
                raise ValidationError("Нельза менять товар в заказе.")
            if db_orderitem.quantity != self.quantity and self.quantity > self.item.quantity:
                raise ValidationError((f"Нет такого количества товара. В заказе {db_orderitem.quantity} шт. "
                                       f"Ещё доступно: {self.item.quantity} шт."))
        else:
            if self.quantity > self.item.quantity:
                raise ValidationError((f"Нет такого количества товара. Доступно: {self.item.quantity} шт."))
        
        return super().clean()

    def change_quantity(self, diff: int):
        """
        Уменьшает количество доступного товара в магазине.
        """
        self.item.quantity -= diff
        self.item.save()
