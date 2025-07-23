from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
import random
import string


class TelegramAuth(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    verification_code = models.CharField(max_length=5)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def generate_code(self):
        self.verification_code = ''.join(random.choices(string.digits, k=5))
        return self.verification_code

    class Meta:
        verbose_name = _('Telegram Auth')
        verbose_name_plural = _('Telegram Auths')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    telegram_chat_id = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
