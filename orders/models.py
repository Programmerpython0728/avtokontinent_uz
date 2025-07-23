from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from shop.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price(self):
        total = sum(item.get_total_price() for item in self.cartitem_set.all())
        return total

    def get_total_items(self):
        return sum(item.quantity for item in self.cartitem_set.all())

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return self.product.get_price_uzs() * self.quantity

    class Meta:
        unique_together = ['cart', 'product']
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')


class PaymentCard(models.Model):
    card_number = models.CharField(max_length=20)
    card_holder = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card_holder} - {self.card_number}"

    class Meta:
        verbose_name = _('Payment Card')
        verbose_name_plural = _('Payment Cards')


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Kutilmoqda')),
        ('payment_confirmed', _('To\'lov tasdiqlandi')),
        ('payment_rejected', _('To\'lov rad etildi')),
        ('preparing', _('Tayyorlanmoqda')),
        ('shipped', _('Yuborildi')),
        ('delivered', _('Yetkazildi')),
        ('cancelled', _('Bekor qilindi')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_receipt = models.ImageField(upload_to='payment_receipts/', blank=True)
    payment_card = models.ForeignKey(PaymentCard, on_delete=models.SET_NULL, null=True)
    delivery_address = models.TextField()
    notes = models.TextField(blank=True)
    oferta_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            self.order_number = f"AK{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total_price(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
