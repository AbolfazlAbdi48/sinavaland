import secrets

from .models import OTP
from .sms_service import send_otp_sms

from django.utils import timezone
from datetime import timedelta


def generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def send_otp(phone_number, user):
    code = generate_otp()

    OTP.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=2)
    )

    return send_otp_sms(phone_number, code)
