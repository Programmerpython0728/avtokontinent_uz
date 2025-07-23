from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('', views.admin_dashboard, name='dashboard'),


    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),


    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),


    path('orders/', views.order_list_admin, name='order_list'),
    path('orders/<int:pk>/', views.order_detail_admin, name='order_detail'),


    path('car-brands/', views.car_brand_list, name='car_brand_list'),
    path('car-brands/create/', views.car_brand_create, name='car_brand_create'),
    path('car-brands/edit/<int:pk>/', views.car_brand_edit, name='car_brand_edit'),
    path('car-brands/delete/<int:pk>/', views.car_brand_delete, name='car_brand_delete'),


    path('car-models/', views.car_model_list, name='car_model_list'),
    path('car-models/create/', views.car_model_create, name='car_model_create'),
    path('car-models/edit/<int:pk>/', views.car_model_edit, name='car_model_edit'),
    path('car-models/delete/<int:pk>/', views.car_model_delete, name='car_model_delete'),


    path('banners/', views.banner_list, name='banner_list'),
    path('banners/create/', views.banner_create, name='banner_create'),
    path('banners/edit/<int:pk>/', views.banner_edit, name='banner_edit'),
    path('banners/delete/<int:pk>/', views.banner_delete, name='banner_delete'),

    path('payment-cards/', views.payment_card_list, name='payment_card_list'),
    path('payment-cards/create/', views.payment_card_create, name='payment_card_create'),
    path('payment-cards/edit/<int:pk>/', views.payment_card_edit, name='payment_card_edit'),
    path('payment-cards/delete/<int:pk>/', views.payment_card_delete, name='payment_card_delete'),
]