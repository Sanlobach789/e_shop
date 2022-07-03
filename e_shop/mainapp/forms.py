from django import forms

from mainapp.models import Category, CategoryFilter


class CategoryForm(forms.ModelForm):
    '''Форма создания/обновления категории'''
    copy_parent_filters = forms.BooleanField(required=False)

    class Meta:
        model = Category
        fields = '__all__'
        exclude = ['filters']

    def save(self, commit):
        # Редактируемая категория
        category: Category = super().save(commit)
        
        # Если checkbox, которые отвечает за 
        # копирование родителльсих фильтров, равен True
        if self.cleaned_data['copy_parent_filters']:
            # Получаем фильтры текущей категории
            current_category_filters = category.categoryfilter_set.all() \
                                               .values_list('filter')
            # Получаем фильтры родительской категории
            parent_category_filters = category.parent_category \
                                              .categoryfilter_set \
                                              .select_related('filter')

            if current_category_filters:
                # Убираем фильтры, которые уже есть у текушей категории
                parent_category_filters = parent_category_filters.exclude(
                    filter__in=current_category_filters
                )

            # Добавляем недостающие фильтры
            for filter in parent_category_filters.all():
                CategoryFilter.objects.create(category=category, filter=filter.filter)

        return category
