import secrets

from django.http.response import JsonResponse

from .models import OTP
from .sms_service import send_otp_sms

from django.utils import timezone
from datetime import timedelta


def send_otp(user):
    code = f"{secrets.randbelow(1_000_000):06d}"
    success = send_otp_sms(user.phone_number, code)

    if not success:
        return False

    OTP.objects.create(
        user=user,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=2)
    )

    return True
