from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Accommodation


def accommodation_list(request):
    """لیست اقامتگاه‌ها"""
    accommodations = Accommodation.objects.order_by('-created_at')

    # فیلتر بر اساس دسته‌بندی
    category = request.GET.get('category')
    if category:
        accommodations = accommodations.filter(category=category)

    # جستجو
    search = request.GET.get('search')
    if search:
        accommodations = accommodations.filter(title__icontains=search) | accommodations.filter(
            location__icontains=search)

    # صفحه‌بندی
    paginator = Paginator(accommodations, 12)
    page = request.GET.get('page')
    accommodations = paginator.get_page(page)

    return render(request, 'accommodations/list.html', {
        'accommodations': accommodations,
        'categories': Accommodation.CATEGORY_CHOICES
    })


def accommodation_detail(request, slug):
    """جزئیات اقامتگاه"""
    accommodation = get_object_or_404(Accommodation, slug=slug)
    user_has_reserved = False
    if request.user.is_authenticated and accommodation.reserved_by == request.user:
        user_has_reserved = True

    return render(request, 'accommodations/detail.html', {
        'accommodation': accommodation,
        'user_has_reserved': user_has_reserved
    })


@login_required
def reserve_accommodation(request, slug):
    accommodation = get_object_or_404(Accommodation, slug=slug)

    if request.user == accommodation.reserved_by:
        messages.warning(request, 'شما قبلاً این اقامتگاه را رزرو کرده‌اید.')
    else:
        accommodation.reserved_by = request.user
        accommodation.is_available = False
        accommodation.save()

        messages.success(request, f'اقامتگاه "{accommodation.title}" رزرو شد.')

    return redirect('accommodations:detail', slug=slug)


@login_required
def cancel_reservation(request, slug):
    accommodation = get_object_or_404(Accommodation, slug=slug)

    accommodation.reserved_by = None
    accommodation.is_available = True
    accommodation.save()

    messages.success(request, 'رزرو لغو شد.')
    return redirect('accommodations:detail', slug=slug)


@login_required
def my_reservations(request):
    accommodations = request.user.reserved_accommodations
    return render(request, 'accommodations/my_reservations.html', {'accommodations': accommodations})
