import django_filters
from .models import Profession


class ProfessionFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(lookup_expr='icontains')
    demand_level = django_filters.NumberFilter()
    demand_level_min = django_filters.NumberFilter(field_name='demand_level', lookup_expr='gte')
    avg_salary_min = django_filters.NumberFilter(field_name='avg_salary', lookup_expr='gte')
    avg_salary_max = django_filters.NumberFilter(field_name='avg_salary', lookup_expr='lte')

    class Meta:
        model = Profession
        fields = ['category', 'demand_level']
