
import django_filters
from django.db.models import Q
from .models import Product, Category, Brand


class ProductFilter(django_filters.FilterSet):
    """فلاتر المنتجات"""
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.filter(is_active=True))
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    featured = django_filters.BooleanFilter()
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'brand', 'price_min', 'price_max', 'featured', 'in_stock']

    def filter_in_stock(self, queryset, name, value):
        """تصفية المنتجات المتوفرة في المخزون"""
        if value:
            return queryset.filter(
                Q(track_quantity=False) | Q(quantity__gt=0)
            )
        return queryset
