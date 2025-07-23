from django.apps import AppConfig
import threading


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
        # Faqat runserver da ishga tushirish
        import sys
        if 'runserver' in sys.argv:
            from django.conf import settings
            if getattr(settings, 'TELEGRAM_BOT_POLLING', False):
                self.start_bot_polling()

    def start_bot_polling(self):
        """Bot polling ni ishga tushirish"""
        try:
            from .utils import start_bot_polling
            start_bot_polling()
        except Exception as e:
            print(f"Bot polling start error: {e}")
