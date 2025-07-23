from django.db import models
from django.utils.translation import gettext_lazy as _


class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.chat_id})"

    class Meta:
        verbose_name = _('Telegram User')
        verbose_name_plural = _('Telegram Users')


class BotMessage(models.Model):
    MESSAGE_TYPES = [
        ('verification', _('Tasdiqlash')),
        ('order_status', _('Buyurtma holati')),
        ('notification', _('Bildirishnoma')),
    ]

    chat_id = models.CharField(max_length=50)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    message_text = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Bot Message')
        verbose_name_plural = _('Bot Messages')
