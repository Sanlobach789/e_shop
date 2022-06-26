import os
from uuid import uuid4

from django.db import models


def path_and_rename(instance, filename):
    upload_to = 'files'
    ext = filename.split('.')[-1]
    # get filename from uuid pk
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)


class Category(models.Model):
    title = models.CharField(max_length=256,)
    image = models.ImageField(upload_to=path_and_rename, blank=True, default="no-avatar.jpg")
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

