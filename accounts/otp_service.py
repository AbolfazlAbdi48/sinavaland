import secrets

from .models import OTP
from .sms_service import send_otp_sms

from django.utils import timezone
from datetime import timedelta


def send_otp(user):
    try:
        code = f"{secrets.randbelow(1_000_000):06d}"

        print("STEP 1 - CODE:", code)
        print("STEP 2 - USERNAME:", repr(user.username))

        success = send_otp_sms(user.username, code)

        print("STEP 3 - SMS SUCCESS:", success)

        if not success:
            return False

        otp = OTP.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=2)
        )

        print("STEP 4 - OTP CREATED:", otp.id)

        return True

    except Exception as e:
        print("SEND OTP ERROR TYPE:", type(e).__name__)
        print("SEND OTP ERROR:", repr(e))
        return False