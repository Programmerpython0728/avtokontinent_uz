from django.core.management.base import BaseCommand
from telegram_bot.utils import process_telegram_updates


class Command(BaseCommand):
    help = 'Telegram bot polling ni ishga tushirish'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Telegram bot polling ishga tushirilmoqda...')
        )

        try:
            process_telegram_updates()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.SUCCESS('🛑 Telegram bot to\'xtatildi.')
            )
