from django import forms

from mainapp.models import Category


class CategoryForm(forms.ModelForm):
    # TODO
    # copy_parent_filters = forms.BooleanField(required=False)

    class Meta:
        model = Category
        fields = '__all__'
        exclude = ['filters']
