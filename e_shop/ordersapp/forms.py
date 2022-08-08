from django import forms
from django.utils.safestring import mark_safe

from e_shop.env import DEBUG
from ordersapp.models import *


class OrderObjectForm(forms.ModelForm):
    basket_link = forms.BooleanField(required=False, disabled=True)

    class Meta:
        model = Order
        fields = ('created_at', 'updated_at', 'finished_at', 'status', 'basket_link', 'customer_data',
                  'comment', 'organization', 'pickup_shop', 'payment_type', 'delivery')

    def __init__(self, *args, **kwargs):
        if DEBUG:
            base_url = "http://127.0.0.1:8000"
        else:
            base_url = "http://"
        super(OrderObjectForm, self).__init__(*args, **kwargs)
        self.fields['basket_link'].label = mark_safe(
            f'<a href="{base_url}/admin/" target="_blank")>Список товаров</a>'
        )
