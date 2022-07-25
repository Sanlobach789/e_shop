from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    phone_number = PhoneNumberField(null=False, blank=True)
