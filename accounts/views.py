from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import User, OTP
from .otp_service import send_otp
from .utils import get_safe_redirect_url


@login_required
def complete_profile(request):
    """ثبت‌نام"""

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save(update_fields=['first_name', 'last_name'])

        next_url = get_safe_redirect_url(request, next_url)

        if next_url:
            return redirect(next_url)

        return redirect('core:home')

    return render(
        request,
        'accounts/complete_profile.html'
    )


def user_login(request):
    """ورود"""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        code = request.POST.get('code')
        next_url = request.POST.get('next')

        if not phone_number or not code:
            messages.error(
                request,
                'شماره موبایل و کد تایید الزامی هستند.'
            )
            return render(request, 'accounts/login.html')

        user = User.objects.filter(phone_number=phone_number).first()

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

        if not user.first_name or not user.last_name:
            if next_url:
                return redirect(
                    f'{reverse("accounts:complete-profile")}?next={next_url}'
                )

            return redirect('accounts:complete-profile')

        next_url = get_safe_redirect_url(request, next_url)

        if next_url:
            return redirect(next_url)

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

    user = User.objects.get_or_create(
        phone_number=phone_number
    )[0]

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

    success = send_otp(user)

    if not success:
        return JsonResponse(
            {"error": "ارسال کد تایید با خطا مواجه شد."},
            status=500,
        )

    return JsonResponse(
        {
            "message": "کد تایید با موفقیت ارسال شد.",
            "retry_after": 60,
        },
        status=200,
    )
