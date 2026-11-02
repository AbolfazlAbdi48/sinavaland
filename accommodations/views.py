import jdatetime

from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from .models import Accommodation
from accounts.sms_service import send_order_sms
from decouple import config

from core.seo import (
    seo_context,
    clean_description,
    price_to_schema,
)


def accommodation_list(request):
    """لیست اقامتگاه‌ها"""

    accommodations = Accommodation.objects.order_by("-created_at")

    # فیلتر بر اساس دسته‌بندی
    category = request.GET.get("category")

    if category:
        accommodations = accommodations.filter(category=category)

    # جستجو
    search = request.GET.get("search")

    if search:
        accommodations = (
                accommodations.filter(title__icontains=search)
                | accommodations.filter(location__icontains=search)
        )

    # صفحه‌بندی
    paginator = Paginator(accommodations, 12)
    page = request.GET.get("page")
    accommodations = paginator.get_page(page)

    context = {
        "accommodations": accommodations,
        "categories": Accommodation.CATEGORY_CHOICES,
    }

    context.update(
        seo_context(
            request,
            title="اقامتگاه‌های مازندران | سینوالند",
            description=(
                "مشاهده هتل‌ها، ویلاها، آپارتمان‌ها و اقامتگاه‌های "
                "بومگردی در مازندران."
            ),
            schema={
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "اقامتگاه‌های سینوالند",
                "description": (
                    "فهرست اقامتگاه‌های ثبت‌شده در سینوالند."
                ),
                "url": request.build_absolute_uri(request.path),
            },
        )
    )

    return render(
        request,
        "accommodations/list.html",
        context,
    )


def accommodation_detail(request, slug):
    """جزئیات اقامتگاه"""

    accommodation = get_object_or_404(
        Accommodation,
        slug=slug,
    )

    user_has_reserved = False

    if (
            request.user.is_authenticated
            and accommodation.reserved_by == request.user
    ):
        user_has_reserved = True

    accommodation_url = request.build_absolute_uri(
        accommodation.get_absolute_url()
    )

    # تصاویر اقامتگاه
    accommodation_images = [
        item
        for item in accommodation.images.all()
        if item.image
    ]

    schema_images = [
        request.build_absolute_uri(item.image.url)
        for item in accommodation_images
    ]

    schema = {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "@id": f"{accommodation_url}#lodging",
        "name": accommodation.title,
        "description": clean_description(
            accommodation.description
        ),
        "url": accommodation_url,
        "address": accommodation.location,
        "numberOfRooms": None,
        "makesOffer": {
            "@type": "Offer",
            "url": accommodation_url,
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "price": format(
                    price_to_schema(
                        accommodation.price_per_night
                    ),
                    "f",
                ),
                "priceCurrency": settings.SEO_PRICE_CURRENCY,
                "unitText": "هر شب",
            },
        },
    }

    # حذف ویژگی‌هایی که مقدار ندارند
    schema = {
        key: value
        for key, value in schema.items()
        if value is not None
    }

    if schema_images:
        schema["image"] = schema_images

    first_image = (
        accommodation_images[0].image
        if accommodation_images
        else None
    )

    context = {
        "accommodation": accommodation,
        "user_has_reserved": user_has_reserved,
    }

    context.update(
        seo_context(
            request,
            title=f"{accommodation.title} | اقامتگاه‌های سینوالند",
            description=accommodation.description,
            image=first_image,
            schema=schema,
        )
    )

    return render(
        request,
        "accommodations/detail.html",
        context,
    )


@login_required
def reserve_accommodation(request, slug):
    accommodation = get_object_or_404(
        Accommodation,
        slug=slug,
    )

    check_in = request.POST.get("check_in")
    check_out = request.POST.get("check_out")

    if not accommodation.is_available:
        messages.warning(
            request,
            "این اقامتگاه در حال حاضر قابل رزرو نیست."
        )
        return redirect(
            "accommodations:detail",
            slug=slug,
        )

    try:
        jy, jm, jd = map(int, check_in.split("/"))
        check_in = jdatetime.date(
            jy, jm, jd
        ).togregorian()

        jy, jm, jd = map(int, check_out.split("/"))
        check_out = jdatetime.date(
            jy, jm, jd
        ).togregorian()

        accommodation.reserved_by = request.user
        accommodation.is_available = False
        accommodation.check_in = check_in
        accommodation.check_out = check_out
        accommodation.status = "pending"

        accommodation.full_clean()
        accommodation.save()

        managers_phone_numbers = config(
            "MANAGER_PHONE_NUMBER"
        ).split(",")

        for number in managers_phone_numbers:
            send_order_sms(
                phone_number=number,
                order_number=accommodation.code,
                full_name=(
                    f"{request.user.first_name} "
                    f"{request.user.last_name}"
                ),
                phone=request.user.username,
            )

    except (TypeError, ValueError):
        messages.error(
            request,
            "تاریخ وارد شده معتبر نیست."
        )
        return redirect(
            "accommodations:detail",
            slug=slug,
        )

    except ValidationError as e:
        for message in e.messages:
            messages.error(request, message)

        return redirect(
            "accommodations:detail",
            slug=slug,
        )

    messages.success(
        request,
        f'اقامتگاه "{accommodation.title}" رزرو شد.'
    )

    return redirect(
        "accommodations:detail",
        slug=slug,
    )


@login_required
def cancel_reservation(request, slug):
    accommodation = get_object_or_404(
        Accommodation,
        slug=slug,
    )

    if request.user != accommodation.reserved_by:
        messages.error(
            request,
            "شما اجازه لغو این رزرو را ندارید."
        )
        return redirect(
            "accommodations:detail",
            slug=slug,
        )

    accommodation.reserved_by = None
    accommodation.is_available = True
    accommodation.status = None
    accommodation.check_in = None
    accommodation.check_out = None
    accommodation.save()

    messages.success(request, "رزرو لغو شد.")

    return redirect(
        "accommodations:detail",
        slug=slug,
    )


@login_required
def my_reservations(request):
    accommodations = request.user.reserved_accommodations

    return render(
        request,
        "accommodations/my_reservations.html",
        {
            "accommodations": accommodations,
        },
    )
