from django.urls import path
from django.http import HttpResponse
from . import views




app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('brand/<slug:slug>/', views.car_brand_detail, name='car_brand_detail'),
    path('brand/<slug:brand_slug>/<slug:model_slug>/', views.car_model_parts, name='car_model_parts'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('like/<int:product_id>/', views.toggle_like, name='toggle_like'),
    path('wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('comment/<int:product_id>/', views.add_comment, name='add_comment'),
]
