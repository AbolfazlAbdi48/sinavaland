from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Estate


def estate_list(request):
    estate = Estate.objects.filter(is_available=True).order_by('start_date')

    duration = request.GET.get('duration')
    if duration:
        estate = estate.filter(duration=duration)

    search = request.GET.get('search')
    if search:
        estate = estate.filter(title__icontains=search) | estate.filter(destination__icontains=search)

    paginator = Paginator(estate, 12)
    page = request.GET.get('page')
    estate = paginator.get_page(page)

    return render(request, 'estate/list.html', {
        'estate': estate,
        'durations': Estate.DURATION_CHOICES,
    })


def estate_detail(request, slug):
    estate = get_object_or_404(Estate, slug=slug, is_available=True)

    user_has_reserved = False
    if request.user.is_authenticated:
        user_has_reserved = request.user in estate.reserved_by.all()

    return render(request, 'estate/detail.html', {
        'estate': estate,
        'user_has_reserved': user_has_reserved,
    })


@login_required
def reserve_estate(request, slug):
    if request.method != 'POST':
        return redirect('estate:detail', slug=slug)

    estate = get_object_or_404(Estate, slug=slug, is_available=True)

    if request.user in estate.reserved_by.all():
        messages.warning(request, 'شما قبلاً این تور را رزرو کرده‌اید.')
    elif estate.available_seats <= 0:
        messages.error(request, 'ظرفیت این تور تکمیل شده است.')
    else:
        estate.reserved_by.add(request.user)
        messages.success(request, f'تور "{estate.title}" با موفقیت رزرو شد.')

    return redirect('estate:detail', slug=slug)


@login_required
def cancel_reservation(request, slug):
    estate = get_object_or_404(Estate, slug=slug)

    if request.user not in estate.reserved_by.all():
        messages.warning(request, 'شما رزروی برای این تور ندارید.')
    else:
        estate.reserved_by.remove(request.user)
        messages.success(request, 'رزرو شما با موفقیت لغو شد.')

    return redirect('estate:detail', slug=slug)


@login_required
def my_reservations(request):
    estate = request.user.reserved_estate.all()
    return render(request, 'estate/my_reservations.html', {'estate': estate})
