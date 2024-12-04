from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from twilio.rest import Client
from .models import Subscriber, FlashSale
import json
import environ
import os

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__),'../.env'))

TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = env('TWILIO_NUMBER')

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def home(request):
    return render(request, 'sms_notifications/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def subscribe(request):
    data = json.loads(request.body)
    phone_number = data.get('phone_number')

    if not phone_number:
        return JsonResponse({'error': 'Phone number is required'}, status=400)

    try:
        Subscriber.objects.create(phone_number=phone_number)
        return JsonResponse({'message': 'Successfully subscribed'})
    except Exception as e:
        return JsonResponse({'error': 'Phone number already subscribed'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def create_sale(request):
    data = json.loads(request.body)

    try:
        flash_sale = FlashSale.objects.create(
            title=data['title'],
            description=data['description'],
            start_time=data['start_time'],
            end_time=data['end_time']
        )

        # Notify subscribers
        notify_subscribers(flash_sale)

        return JsonResponse({
            'message': 'Flash sale created',
            'sale_id': flash_sale.id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def notify_subscribers(flash_sale):
    subscribers = Subscriber.objects.all()
    message = f"🔥 Flash Sale Alert! 🔥\n{flash_sale.title}\n{flash_sale.description}"

    for subscriber in subscribers:
        try:
            twilio_client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to=subscriber.phone_number
            )
        except Exception as e:
            print(f"Error sending SMS to {subscriber.phone_number}: {str(e)}")