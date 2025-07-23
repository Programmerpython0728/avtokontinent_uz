from django.http import  JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from .utils import handle_telegram_update  # Bu yerda o'zgardi

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramWebhookView(View):
    def post(self, request):
        try:
            update_data = json.loads(request.body.decode('utf-8'))


            logger.info(f"Telegram webhook received: {update_data}")

            handle_telegram_update(update_data)  # Bu yerda ham o'zgardi

            return JsonResponse({'status': 'ok'})

        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Webhook error: {str(e)}")
            return JsonResponse({'error': 'Internal error'}, status=500)

    def get(self, request):
        return JsonResponse({
            'status': 'Telegram webhook endpoint',
            'method': 'POST required'
        })


telegram_webhook = TelegramWebhookView.as_view()


@csrf_exempt
@require_POST
def telegram_webhook_simple(request):
    try:
        update_data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Telegram webhook received: {update_data}")

        handle_telegram_update(update_data)

        return JsonResponse({'status': 'ok'})

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return JsonResponse({'error': 'Internal error'}, status=500)
