# accounts/sms_service.py
import requests
from decouple import config

# Load your secret credentials from the .env file
API_KEY = config('SMS_IR_API_KEY')
OTP_TEMPLATE_ID = config('SMS_IR_OTP_TEMPLATE_ID')
ORDER_TEMPLATE_ID = config('SMS_IR_ORDER_TEMPLATE_ID')

# Define the API endpoint
API_URL = "https://api.sms.ir/v1/send/verify"


def send_otp_sms(phone_number, code):
    payload = {
        "mobile": phone_number,
        "templateId": OTP_TEMPLATE_ID,
        "parameters": [
            {
                "name": "CODE",
                "value": code,
            }
        ],
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "x-api-key": API_KEY,
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )

        if response.status_code == 200:
            return True

        return False

    except requests.RequestException:
        return False

def send_order_sms(phone_number, order_number, full_name, phone):
    payload = {
        "mobile": phone_number,
        "templateId": ORDER_TEMPLATE_ID,
        "parameters": [
            {
                "name": "ORDER_NUMBER",
                "value": str(order_number)
            },
            {
                "name": "FULLNAME",
                "value": str(full_name)
            },
            {
                "name": "PHONE",
                "value": str(phone)
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/plain',
        'x-api-key': API_KEY
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"Successfully sent order SMS to {phone_number}. Response: {response.text}")
            return True
        else:
            print(
                f"Error sending order SMS to {phone_number}. Status: {response.status_code}, Response: {response.text}")
            return False

    except Exception as e:
        print(f"SMS service error: {e}")
        return False
