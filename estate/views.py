from decimal import Decimal, InvalidOperation

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q, Prefetch

from .models import Estate

from core.seo import (
    seo_context,
    clean_description,
    price_to_schema,
)


def estate_list(request):
    """لیست املاک"""

    estate = (
        Estate.objects
        .filter(is_available=True)
        .prefetch_related(
            Prefetch(
                "images",
                to_attr="prefetched_images",
            )
        )
        .order_by("-created_at")
    )

    # ===== Price Filters =====
    lowest_price = request.GET.get(
        "lowest_price", ""
    ).strip()

    highest_price = request.GET.get(
        "highest_price", ""
    ).strip()

    try:
        lowest_price = (
            Decimal(lowest_price)
            if lowest_price
            else None
        )

        highest_price = (
            Decimal(highest_price)
            if highest_price
            else None
        )

        for price in (lowest_price, highest_price):
            if price is not None and (
                    not price.is_finite() or price < 0
            ):
                raise InvalidOperation

        if (
                lowest_price is not None
                and highest_price is not None
                and lowest_price > highest_price
        ):
            raise InvalidOperation

    except InvalidOperation:
        messages.error(
            request,
            "لطفاً بازه قیمت را با مقادیر عددی معتبر وارد کنید."
        )

        lowest_price = None
        highest_price = None

    if lowest_price is not None:
        estate = estate.filter(
            total_price__gte=lowest_price
        )

    if highest_price is not None:
        estate = estate.filter(
            total_price__lte=highest_price
        )

    # ===== Search =====
    search = request.GET.get("search", "").strip()

    if search:
        estate = estate.filter(
            Q(title__icontains=search)
            | Q(destination__icontains=search)
        )

    # ===== Pagination =====
    paginator = Paginator(estate, 12)

    page = request.GET.get("page")

    estate = paginator.get_page(page)

    # ===== Context =====
    context = {
        "estate": estate,
    }

    # ===== SEO =====
    context.update(
        seo_context(
            request,
            title="املاک مازندران | سینوالند",
            description=(
                "مشاهده آگهی‌های خرید و فروش ملک در مازندران "
                "در سامانه املاک سینوالند."
            ),
            schema={
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "املاک سینوالند",
                "description": (
                    "فهرست آگهی‌های املاک ثبت‌شده در سینوالند."
                ),
                "url": request.build_absolute_uri(
                    request.path
                ),
            },
        )
    )

    return render(
        request,
        "estate/list.html",
        context,
    )


def estate_detail(request, slug):
    """جزئیات ملک"""

    estate = get_object_or_404(
        Estate.objects.prefetch_related(
            Prefetch(
                "images",
                to_attr="prefetched_images",
            )
        ),
        slug=slug,
        is_available=True,
    )

    estate_url = request.build_absolute_uri(
        estate.get_absolute_url()
    )

    description = clean_description(
        estate.description
    )

    # ===== Estate Images =====
    estate_images = [
        item
        for item in estate.prefetched_images
        if item.image
    ]

    image_urls = [
        request.build_absolute_uri(item.image.url)
        for item in estate_images
    ]

    # ===== Main Property Entity =====
    property_schema = {
        "@type": "Place",
        "@id": f"{estate_url}#property",
        "name": estate.title,
        "description": description,
        "address": {
            "@type": "PostalAddress",
            "addressLocality": estate.destination,
            "addressCountry": "IR",
        },
    }

    if image_urls:
        property_schema["image"] = image_urls

    # ===== Property Attributes =====
    additional_properties = []

    property_attributes = [
        ("متراژ", estate.area, "متر مربع"),
        ("تعداد اتاق", estate.rooms, None),
        ("طبقه", estate.floor, None),
        ("سال ساخت", estate.construction_year, None),
    ]

    for name, value, unit in property_attributes:
        if value is not None:
            property_value = {
                "@type": "PropertyValue",
                "name": name,
                "value": value,
            }

            if unit:
                property_value["unitText"] = unit

            additional_properties.append(
                property_value
            )

    # ===== Property Features =====
    features = {
        "استخر": estate.has_pool,
        "پارکینگ": estate.has_parking,
        "انباری": estate.has_storage,
    }

    for name, value in features.items():
        additional_properties.append({
            "@type": "PropertyValue",
            "name": name,
            "value": "دارد" if value else "ندارد",
        })

    if additional_properties:
        property_schema["additionalProperty"] = (
            additional_properties
        )

    # ===== Offer Schema =====
    offer_schema = {
        "@type": "Offer",
        "url": estate_url,
        "itemOffered": {
            "@id": f"{estate_url}#property",
        },
        "availability": "https://schema.org/InStock",
        "businessFunction": (
            "https://purl.org/goodrelations/v1#Sell"
        ),
    }

    if estate.total_price is not None:
        offer_schema.update({
            "price": price_to_schema(
                estate.total_price
            ),
            "priceCurrency": "IRR",
        })

    # ===== Real Estate Listing Schema =====
    schema = {
        "@context": "https://schema.org",
        "@type": "RealEstateListing",
        "@id": f"{estate_url}#listing",
        "name": estate.title,
        "description": description,
        "url": estate_url,
        "datePosted": estate.created_at.isoformat(),
        "mainEntity": property_schema,
        "offers": offer_schema,
        "inLanguage": "fa-IR",
    }

    # ===== SEO Image =====
    first_image = (
        estate_images[0].image
        if estate_images
        else None
    )

    # ===== Context =====
    context = {
        "estate": estate,
        "estate_images": estate_images,
    }

    # ===== SEO =====
    context.update(
        seo_context(
            request,
            title=f"{estate.title} | املاک سینوالند",
            description=description,
            image=first_image,
            schema=schema,
            canonical_url=estate_url,
        )
    )

    return render(
        request,
        "estate/detail.html",
        context,
    )
