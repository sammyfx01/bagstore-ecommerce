import requests
from django.conf import settings

PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_payment(email, amount_naira, reference, callback_url):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": int(amount_naira * 100),
        "reference": reference,
        "callback_url": callback_url,
    }
    response = requests.post(f"{PAYSTACK_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    return response.json()


def verify_payment(reference):
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers)
    return response.json()