from django import forms

from mainapp.models import ItemProperty, CategoryFilterValue, Item, Category


NONE_VALUE_TEXT = '---------'


class ItemPropertyForm(forms.ModelForm):
    """Форма просмтора/создания свойства (фильтра) товара"""
    class Meta:
        model = ItemProperty
        fields = '__all__'

    def get_initial_for_field(self, field, field_name):
        if field_name == 'value':
            if self.instance and self.instance.id:
                # Получаем возможные, доступные значения для товара
                available_values = (
                    CategoryFilterValue.objects
                    .select_related('filter')\
                        .filter(
                            filter=self.instance.filter,
                            category=self.instance.item.category
                        )
                )
                # Добавляем дефолтное значение
                available_values = (
                    [(None, NONE_VALUE_TEXT)]
                    + list(map(lambda x: (x.id, x.name), available_values))
                )
                field.choices =  available_values
        return super().get_initial_for_field(field, field_name)    


class ItemForm(forms.ModelForm):
    """Форма просмтора/создания товара"""
    add_quantity = forms.IntegerField(label='Добавить количество', required=False,
                                      widget=forms.NumberInput(attrs={'required': False}))

    class Meta:
        model = Item
        fields = '__all__'

    def get_initial_for_field(self, field, field_name):
        if field_name == 'category':
            # Получаем возможные, доступные категории для товара
            available_categories = Category.get_non_node_categories()
            # Добавляем дефолтное значение
            available_categories = (
                [(None, NONE_VALUE_TEXT)]
                + list(map(lambda x: (x.id, x.name), available_categories))
            )
            field.choices =  available_categories
        elif field_name == 'quantity':
            field.widget.attrs['readonly'] = self.instance.pk is not None
            field.widget.attrs['required'] = False
        return super().get_initial_for_field(field, field_name)

    def save(self, commit):
        if self.cleaned_data.get('add_quantity', 0):
            self.instance.quantity += self.cleaned_data.get('add_quantity', 0)
        return super().save(commit)


class CategoryFilterValueForm(forms.ModelForm):
    """Форма просмтора/создания значений фильтров"""
    class Meta:
        model = CategoryFilterValue
        fields = '__all__'

    def get_initial_for_field(self, field, field_name):
        if field_name == 'category':
            # Получаем возможные, доступные категории для товара
            available_categories = Category.get_non_node_categories()
            # Добавляем дефолтное значение
            available_categories = (
                [(None, NONE_VALUE_TEXT)]
                + list(map(lambda x: (x.id, x.name), available_categories))
            )
            field.choices =  available_categories
        return super().get_initial_for_field(field, field_name)


class CategoryForm(forms.ModelForm):
    """Форма просмтора/создания категорий"""
    class Meta:
        model = Category
        fields = '__all__'

    def get_initial_for_field(self, field, field_name):
        if field_name == 'parent_category':
            # Получаем возможные, доступные категории-родители
            available_categories = Category.get_node_categories()
            # Добавляем дефолтное значение
            available_categories = (
                [(None, NONE_VALUE_TEXT)]
                + list(map(lambda x: (x.id, x.name), available_categories))
            )
            field.choices = available_categories
        return super().get_initial_for_field(field, field_name)
