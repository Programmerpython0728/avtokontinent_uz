from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/', views.telegram_webhook, name='webhook'),
]
