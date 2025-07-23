from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from datetime import timedelta
from .models import TelegramAuth, UserProfile
import logging

logger = logging.getLogger(__name__)

try:
    import requests
    from telegram_bot.utils import send_telegram_message, send_contact_request, \
        send_verification_code as actual_send_verification_code

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("Requests library or telegram_bot.utils not available. Telegram bot functionality might be limited.")


    def send_telegram_message(chat_id, message):
        logger.info(f"Mock: Sending message to {chat_id}: {message[:50]}...")
        return None


    def send_contact_request(chat_id, message):
        logger.info(f"Mock: Sending contact request to {chat_id}: {message[:50]}...")
        return None


    def actual_send_verification_code(phone_number, code):
        logger.info(f"Mock: Sending verification code {code} to {phone_number}")
        return False


def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            # Telefon raqamni tozalash
            phone_number = phone_number.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone_number.startswith('+'):
                phone_number = '+998' + phone_number

            logger.info(f"Login attempt for phone: {phone_number}")

            telegram_auth, created = TelegramAuth.objects.get_or_create(
                phone_number=phone_number,
                defaults={
                    'expires_at': timezone.now() + timedelta(minutes=5)
                }
            )

            if not created:
                telegram_auth.expires_at = timezone.now() + timedelta(minutes=5)
                telegram_auth.is_verified = False

            code = telegram_auth.generate_code()
            telegram_auth.save()

            logger.info(f"Generated code {code} for {phone_number}. TelegramAuth ID: {telegram_auth.id}")

            if REQUESTS_AVAILABLE:
                success = actual_send_verification_code(phone_number, code)
                if success:
                    logger.info(f"Verification code sent to Telegram for {phone_number}")
                else:
                    logger.error(
                        f"Failed to send verification code to Telegram for {phone_number}. User might not have interacted with the bot or chat ID is missing.")
                    messages.error(request,
                                   _('Tasdiqlash kodini yuborishda xatolik yuz berdi. Iltimos, Telegram botimizga /start buyrug\'ini yuboring va raqamingizni tasdiqlang.'))
                    return redirect('accounts:login')
            else:
                logger.warning(f"Requests not available. Code for {phone_number}: {code}")
                messages.warning(request, _('Telegram bot funksiyasi mavjud emas. Kod: ') + code)

            request.session['auth_phone'] = phone_number
            return redirect('accounts:verify_code')
        else:
            messages.error(request, _('Telefon raqamini kiriting.'))

    return render(request, 'accounts/login.html')


def verify_code(request):
    phone_number = request.session.get('auth_phone')
    if not phone_number:
        return redirect('accounts:login')

    if request.method == 'POST':
        code = request.POST.get('code')
        logger.info(f"Verification attempt for phone: {phone_number} with code: {code}")
        try:
            telegram_auth = TelegramAuth.objects.get(
                phone_number=phone_number,
                verification_code=code,
                expires_at__gt=timezone.now()
            )

            user, created = User.objects.get_or_create(
                username=phone_number,
                defaults={
                    'first_name': phone_number,
                }
            )

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': phone_number,
                    'telegram_chat_id': telegram_auth.telegram_chat_id  # Chat ID ni saqlash
                }
            )

            if profile.telegram_chat_id != telegram_auth.telegram_chat_id:
                profile.telegram_chat_id = telegram_auth.telegram_chat_id
                profile.save()

            telegram_auth.is_verified = True
            telegram_auth.save()

            login(request, user)

            if REQUESTS_AVAILABLE and telegram_auth.telegram_chat_id:
                from telegram_bot.utils import send_telegram_message as actual_send_telegram_message
                actual_send_telegram_message(telegram_auth.telegram_chat_id,
                                             _("✅ AvtoKontinent.uz saytiga muvaffaqiyatli kirdingiz!"))

            messages.success(request, _('Muvaffaqiyatli kirdingiz!'))

            # Redirect to next page or home
            next_url = request.session.get('next_url', 'shop:home')
            if 'next_url' in request.session:
                del request.session['next_url']

            return redirect(next_url)

        except TelegramAuth.DoesNotExist:
            logger.warning(f"Invalid code or expired for {phone_number} with code {code}")
            messages.error(request, _('Noto\'g\'ri kod yoki kod muddati tugagan.'))

    context = {
        'phone_number': phone_number,
        'telegram_bot_url': settings.TELEGRAM_BOT_URL
    }
    return render(request, 'accounts/verify_code.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, _('Muvaffaqiyatli chiqdingiz!'))
    return redirect('shop:home')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.save()

        profile.address = request.POST.get('address', '')
        profile.save()

        messages.success(request, _('Profil muvaffaqiyatli yangilandi!'))

    context = {
        'profile': profile
    }
    return render(request, 'accounts/profile.html', context)

