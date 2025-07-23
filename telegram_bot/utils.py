import requests
import time
import threading
import json
from django.conf import settings
from .models import TelegramUser, BotMessage
from orders.models import Order


def send_telegram_message(chat_id, message):
    """Telegram bot orqali xabar yuborish"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }

    print(f"🔄 Sending message to {chat_id}: {message[:50]}...")

    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result.get('ok'):
            print(f"✅ Message sent successfully to {chat_id}")
            return result
        else:
            print(f"❌ Failed to send message: {result.get('description')}")
            print(f"Full response: {result}")
            return None
    except Exception as e:
        print(f"💥 Telegram message send error: {e}")
        return None


def get_updates(offset=None):
    """Telegram bot yangilanishlarini olish (polling)"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    params = {
        'timeout': 30,  # 30 soniya kutish
        'limit': 100
    }

    if offset:
        params['offset'] = offset

    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json()
    except Exception as e:
        print(f"Get updates error: {e}")
        return None


def process_telegram_updates():
    """Telegram yangilanishlarini qayta ishlash (polling uchun)"""
    last_update_id = 0
    print("🚀 Starting Telegram bot polling...")

    while True:
        try:
            result = get_updates(last_update_id + 1)

            if result and result.get('ok'):
                updates = result.get('result', [])

                if updates:
                    print(f"📨 Received {len(updates)} updates")

                for update in updates:
                    last_update_id = update['update_id']
                    print(f"🔄 Processing update {last_update_id}")
                    handle_telegram_update(update)

            time.sleep(1)  # 1 soniya kutish

        except KeyboardInterrupt:
            print("🛑 Bot to'xtatildi")
            break
        except Exception as e:
            print(f"💥 Polling error: {e}")
            time.sleep(5)  # Xatolik bo'lsa 5 soniya kutish


def handle_telegram_update(update):
    """
    Telegram yangilanishini qayta ishlash
    Bu funksiya ham webhook, ham polling uchun ishlatiladi
    """
    try:
        message = update.get('message', {})
        chat_id = str(message.get('chat', {}).get('id', ''))
        text = message.get('text', '')

        print(f"📩 Received message from {chat_id}: {text}")

        if not chat_id:
            return

        if text == '/start':
            print(f"🆕 New user started bot: {chat_id}")
            # Foydalanuvchini ro'yxatga olish
            user_data = message.get('from', {})
            telegram_user, created = TelegramUser.objects.get_or_create(
                chat_id=chat_id,
                defaults={
                    'username': user_data.get('username', ''),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                }
            )

            welcome_message = """
🚗 <b>AvtoKontinent.uz</b> botiga xush kelibsiz!

Bu bot orqali:
✅ Saytga kirish uchun tasdiqlash kodini olasiz
📦 Buyurtmalaringiz holati haqida xabar olasiz

<b>Telefon raqamingizni yuboring:</b>
Masalan: +998901234567

Yoki pastdagi tugma orqali kontaktingizni yuboring 👇
            """

            # Kontakt so'rash tugmasi bilan
            send_contact_request(chat_id, welcome_message)

        elif message.get('contact'):
            print(f"📱 Contact received from {chat_id}")
            # Kontakt ma'lumotlarini saqlash
            contact = message['contact']
            phone_number = contact['phone_number']

            # Telefon raqamni formatlash
            if not phone_number.startswith('+'):
                phone_number = '+' + phone_number

            telegram_user = TelegramUser.objects.filter(chat_id=chat_id).first()
            if telegram_user:
                telegram_user.phone_number = phone_number
                telegram_user.save()
                print(f"💾 Saved phone number {phone_number} for {chat_id}")

                # Accounts app da telegram_chat_id ni yangilash
                from accounts.models import TelegramAuth
                telegram_auth = TelegramAuth.objects.filter(phone_number=phone_number).first()
                if telegram_auth:
                    telegram_auth.telegram_chat_id = chat_id
                    telegram_auth.save()
                    print(f"🔗 Linked phone {phone_number} with chat {chat_id}")

                success_message = f"✅ <b>Telefon raqamingiz saqlandi:</b> {phone_number}\n\nEndi saytda tasdiqlash kodini kiritishingiz mumkin."
                send_telegram_message(chat_id, success_message)
            else:
                error_message = "❌ Avval /start buyrug'ini yuboring."
                send_telegram_message(chat_id, error_message)

        elif text.startswith('+998') or text.startswith('998') or text.startswith('+'):
            print(f"📞 Phone number received from {chat_id}: {text}")
            # Telefon raqam matn sifatida yuborilgan
            phone_number = text.strip()
            if not phone_number.startswith('+'):
                if phone_number.startswith('998'):
                    phone_number = '+' + phone_number
                else:
                    phone_number = '+998' + phone_number

            telegram_user = TelegramUser.objects.filter(chat_id=chat_id).first()
            if telegram_user:
                telegram_user.phone_number = phone_number
                telegram_user.save()
                print(f"💾 Saved phone number {phone_number} for {chat_id}")

                from accounts.models import TelegramAuth
                telegram_auth = TelegramAuth.objects.filter(phone_number=phone_number).first()
                if telegram_auth:
                    telegram_auth.telegram_chat_id = chat_id
                    telegram_auth.save()
                    print(f"🔗 Linked phone {phone_number} with chat {chat_id}")

                success_message = f"✅ <b>Telefon raqamingiz saqlandi:</b> {phone_number}\n\nEndi saytda tasdiqlash kodini kiritishingiz mumkin."
                send_telegram_message(chat_id, success_message)
            else:
                error_message = "❌ Avval /start buyrug'ini yuboring."
                send_telegram_message(chat_id, error_message)

        else:
            # Noma'lum xabar
            help_message = """
❓ <b>Yordam:</b>

/start - Botni qayta ishga tushirish
📱 Telefon raqamingizni yuboring
📞 Yoki kontakt tugmasini bosing

<b>Masalan:</b> +998901234567
            """
            send_telegram_message(chat_id, help_message)

    except Exception as e:
        print(f"💥 Telegram update handling error: {e}")


def send_contact_request(chat_id, message):
    """Kontakt so'rash tugmasi bilan xabar yuborish"""
    bot_token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    keyboard = {
        "keyboard": [
            [{"text": "📱 Kontaktni yuborish", "request_contact": True}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps(keyboard)
    }

    try:
        response = requests.post(url, data=data)
        result = response.json()
        if result.get('ok'):
            print(f"✅ Contact request sent to {chat_id}")
        else:
            print(f"❌ Failed to send contact request: {result.get('description')}")
        return result
    except Exception as e:
        print(f"💥 Contact request send error: {e}")
        return None


def send_verification_code(phone_number, code):
    """Tasdiqlash kodini yuborish"""
    from accounts.models import TelegramAuth

    print(f"🔐 Attempting to send verification code to {phone_number}")

    try:
        telegram_auth = TelegramAuth.objects.filter(phone_number=phone_number).first()
        if telegram_auth and telegram_auth.telegram_chat_id:
            print(f"📨 Found chat_id {telegram_auth.telegram_chat_id} for {phone_number}")
            message = f"""
🔐 <b>AvtoKontinent.uz tasdiqlash kodi:</b>

<code>{code}</code>

⏰ Kod 5 daqiqa davomida amal qiladi.
🌐 Kodni saytda kiriting.
            """

            result = send_telegram_message(telegram_auth.telegram_chat_id, message)
            return result is not None
        else:
            print(f"❌ Chat ID not found for {phone_number}")
            return False
    except Exception as e:
        print(f"💥 Verification code send error: {e}")
        return False


def send_order_status_update(order, status_type):
    """Buyurtma holati haqida xabar yuborish"""
    print(f"📦 Sending order status update: {order.order_number} - {status_type}")

    try:
        user_profile = order.user.userprofile
        chat_id = user_profile.telegram_chat_id

        if not chat_id:
            print(f"❌ No chat_id found for user {order.user.username}")
            return

        messages = {
            'payment_uploaded': f"""
📋 <b>Buyurtma #{order.order_number}</b>

✅ To'lov cheki qabul qilindi. 
⏳ Tez orada tekshirib ko'ramiz.
            """,
            'payment_confirmed': f"""
📋 <b>Buyurtma #{order.order_number}</b>

✅ <b>To'lovingiz tasdiqlandi!</b>
📦 Buyurtma tayyorlanmoqda.
📅 Taxminiy yetkazilish vaqti: 2 kun.
            """,
            'payment_rejected': f"""
📋 <b>Buyurtma #{order.order_number}</b>

❌ <b>To'lovingiz tasdiqlanmadi.</b>
🔄 Iltimos, qaytadan urinib ko'ring.
            """,
            'preparing': f"""
📋 <b>Buyurtma #{order.order_number}</b>

📦 <b>Buyurtmangiz tayyorlanmoqda.</b>
            """,
            'shipped': f"""
📋 <b>Buyurtma #{order.order_number}</b>

🚚 <b>Buyurtmangiz yuborildi!</b>
📍 Tez orada yetkaziladi.
            """,
            'delivered': f"""
📋 <b>Buyurtma #{order.order_number}</b>

✅ <b>Buyurtmangiz yetkazildi!</b>
🙏 Xaridingiz uchun rahmat!
            """
        }

        message = messages.get(status_type, f"Buyurtma #{order.order_number} holati yangilandi.")

        # Xabarni yuborish
        result = send_telegram_message(chat_id, message)

        # Xabar logini saqlash
        BotMessage.objects.create(
            chat_id=chat_id,
            message_type='order_status',
            message_text=message,
            is_sent=result is not None
        )

        print(f"📝 Order status message logged for {order.order_number}")

    except Exception as e:
        print(f"💥 Order status update error: {e}")


# Bot polling ni ishga tushirish uchun
def start_bot_polling():
    """Bot polling ni alohida thread da ishga tushirish"""
    bot_thread = threading.Thread(target=process_telegram_updates, daemon=True)
    bot_thread.start()
    print("🤖 Telegram bot polling started...")


# Webhook uchun ham, polling uchun ham ishlaydigan umumiy funksiya
# Bu eski nom bilan ham qoldirildi, agar boshqa joylarda ishlatilgan bo'lsa
def handle_telegram_webhook(update_data):
    """Eski nom - yangi funksiyaga yo'naltirish"""
    return handle_telegram_update(update_data)
