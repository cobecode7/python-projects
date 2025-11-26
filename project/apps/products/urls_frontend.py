
from django.urls import path
from . import views

urlpatterns = [
    # صفحة قائمة المنتجات
    path('', views.ProductListView.as_view(), name='product_list'),

    # صفحة تفاصيل المنتج
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),

    # صفحة قائمة الفئات
    path('categories/', views.CategoryListView.as_view(), name='category_list'),

    # صفحة تفاصيل الفئة
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),

    # صفحة قائمة العلامات التجارية
    path('brands/', views.BrandListView.as_view(), name='brand_list'),

    # صفحة تفاصيل العلامة التجارية
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),

    # صفحة البحث
    path('search/', views.SearchView.as_view(), name='search'),
]
