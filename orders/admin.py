from django.contrib import admin
from django.utils.html import format_html
from .models import *

try:
    from telegram_bot.utils import send_order_status_update

    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


    def send_order_status_update(order, status_type):
        print(f"Telegram not available. Order {order.order_number} status: {status_type}")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_amount', 'created_at', 'payment_receipt_display']
    list_filter = ['status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__first_name']
    readonly_fields = ['order_number', 'user', 'total_amount', 'created_at']
    inlines = [OrderItemInline]
    actions = ['confirm_payment', 'reject_payment', 'mark_as_preparing', 'mark_as_shipped', 'mark_as_delivered']

    def payment_receipt_display(self, obj):
        if obj.payment_receipt:
            return format_html('<a href="{}" target="_blank">Ko\'rish</a>', obj.payment_receipt.url)
        return "Yuklanmagan"

    payment_receipt_display.short_description = 'To\'lov cheki'

    def confirm_payment(self, request, queryset):
        for order in queryset:
            order.status = 'payment_confirmed'
            order.save()
            if TELEGRAM_AVAILABLE:
                send_order_status_update(order, 'payment_confirmed')
        self.message_user(request, f"{queryset.count()} ta buyurtma to'lovi tasdiqlandi.")

    confirm_payment.short_description = "To'lovni tasdiqlash"

    def reject_payment(self, request, queryset):
        for order in queryset:
            order.status = 'payment_rejected'
            order.save()
            if TELEGRAM_AVAILABLE:
                send_order_status_update(order, 'payment_rejected')
        self.message_user(request, f"{queryset.count()} ta buyurtma to'lovi rad etildi.")

    reject_payment.short_description = "To'lovni rad etish"

    def mark_as_preparing(self, request, queryset):
        for order in queryset:
            order.status = 'preparing'
            order.save()
            if TELEGRAM_AVAILABLE:
                send_order_status_update(order, 'preparing')
        self.message_user(request, f"{queryset.count()} ta buyurtma tayyorlanmoqda deb belgilandi.")

    mark_as_preparing.short_description = "Tayyorlanmoqda deb belgilash"

    def mark_as_shipped(self, request, queryset):
        for order in queryset:
            order.status = 'shipped'
            order.save()
            if TELEGRAM_AVAILABLE:
                send_order_status_update(order, 'shipped')
        self.message_user(request, f"{queryset.count()} ta buyurtma yuborildi deb belgilandi.")

    mark_as_shipped.short_description = "Yuborildi deb belgilash"

    def mark_as_delivered(self, request, queryset):
        for order in queryset:
            order.status = 'delivered'
            order.save()
            if TELEGRAM_AVAILABLE:
                send_order_status_update(order, 'delivered')
        self.message_user(request, f"{queryset.count()} ta buyurtma yetkazildi deb belgilandi.")

    mark_as_delivered.short_description = "Yetkazildi deb belgilash"


@admin.register(PaymentCard)
class PaymentCardAdmin(admin.ModelAdmin):
    list_display = ['card_holder', 'card_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['card_holder', 'card_number']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'created_at', 'get_total_items']
    list_filter = ['created_at']
    search_fields = ['user__username']

    def get_total_items(self, obj):
        return obj.get_total_items()

    get_total_items.short_description = 'Jami mahsulotlar'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name_uz']
