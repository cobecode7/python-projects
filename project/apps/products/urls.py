
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'brands', views.BrandViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'reviews', views.ProductReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('featured/', views.FeaturedProductsView.as_view(), name='featured_products'),
    path('category/<slug:slug>/', views.CategoryProductsView.as_view(), name='category_products'),
    path('brand/<slug:slug>/', views.BrandProductsView.as_view(), name='brand_products'),
    path('tag/<slug:slug>/', views.TagProductsView.as_view(), name='tag_products'),
]
