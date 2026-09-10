from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import User, OTP
from .otp_service import send_otp


def register(request):
    """ثبت‌نام"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'این نام کاربری قبلاً استفاده شده است.')
            return redirect('accounts:register')

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password
        )

        if phone_number:
            user.phone_number = phone_number

        user.set_password(password)

        try:
            user.full_clean()
        except ValidationError as e:
            for message in e.messages:
                messages.error(request, message)
            return render(request, 'accounts/register.html')

        user.save()

        login(request, user)
        messages.success(request, 'ثبت‌نام با موفقیت انجام شد.')
        return redirect('core:home')

    return render(request, 'accounts/register.html')


def user_login(request):
    """ورود"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        code = request.POST.get('code')

        if not phone_number or not code:
            messages.error(
                request,
                'شماره موبایل و کد تایید الزامی هستند.'
            )
            return render(request, 'accounts/login.html')

        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            messages.error(
                request,
                'کاربری با این شماره موبایل وجود ندارد.'
            )
            return render(request, 'accounts/login.html')

        otp = OTP.objects.filter(
            user=user,
            code=code,
            is_used=False
        ).order_by('-created_at').first()

        if not otp:
            messages.error(
                request,
                'کد وارد شده صحیح نیست.'
            )
            return render(request, 'accounts/login.html')

        if timezone.now() >= otp.expires_at:
            messages.error(
                request,
                'کد تایید منقضی شده است.'
            )
            return render(request, 'accounts/login.html')

        otp.is_used = True
        otp.save(update_fields=['is_used'])

        login(request, user)

        messages.success(request, 'خوش آمدید!')
        return redirect('core:home')

    return render(request, 'accounts/login.html')


def user_logout(request):
    """خروج"""
    logout(request)
    messages.success(request, 'با موفقیت خارج شدید.')
    return redirect('core:home')


@login_required
def profile(request):
    """پروفایل کاربر"""
    return render(request, 'accounts/profile.html')


@require_POST
def request_otp(request):
    phone_number = request.POST.get("phone_number")

    if not phone_number:
        return JsonResponse(
            {"error": "شماره موبایل الزامی است."},
            status=400,
        )

    user = User.objects.filter(phone_number=phone_number).first()

    if not user:
        return JsonResponse(
            {"error": "کاربری با این شماره موبایل وجود ندارد."},
            status=404,
        )

    last_otp = OTP.objects.filter(user=user).order_by('-created_at').first()

    if last_otp:
        elapsed = timezone.now() - last_otp.created_at

        if elapsed < timedelta(seconds=60):
            remaining = 60 - int(elapsed.total_seconds())

            return JsonResponse(
                {
                    "error": 'لطفاً کمی صبر کنید.',
                    "retry_after": max(remaining, 1),
                },
                status=429,
            )

    send_otp(phone_number, user)

    return JsonResponse({
        "message": "کد تایید ارسال شد.",
        "retry_after": 60,
    })
