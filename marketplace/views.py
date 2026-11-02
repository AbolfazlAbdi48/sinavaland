from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Product
from cart import services

from core.seo import (
    seo_context,
    clean_description,
    product_offer,
)


def product_list(request):
    """لیست محصولات"""

    products = Product.objects.filter(
        is_available=True,
        stock__gt=0,
    ).order_by("-created_at")

    # فیلتر بر اساس دسته‌بندی
    category = request.GET.get("category")

    if category:
        products = products.filter(category=category)

    # جستجو
    search = request.GET.get("search")

    if search:
        products = (
                products.filter(title__icontains=search)
                | products.filter(description__icontains=search)
        )

    # صفحه‌بندی
    paginator = Paginator(products, 12)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    context = {
        "products": products,
        "categories": Product.CATEGORY_CHOICES,
    }

    context.update(
        seo_context(
            request,
            title="بازارچه محصولات | سینوالند",
            description=(
                "خرید محصولات، سوغات و صنایع دستی مازندران "
                "از بازارچه سینوالند."
            ),
            schema={
                "@context": "https://schema.org",
                "@type": "CollectionPage",
                "name": "بازارچه محصولات سینوالند",
                "description": (
                    "مشاهده و خرید محصولات و سوغات مازندران."
                ),
                "url": request.build_absolute_uri(request.path),
            },
        )
    )

    return render(
        request,
        "marketplace/list.html",
        context,
    )


def product_detail(request, slug):
    """جزئیات محصول"""

    product = get_object_or_404(
        Product,
        slug=slug,
        is_available=True,
        stock__gt=0,
    )

    is_in_cart = False

    if request.user.is_authenticated:
        cart = services.get_cart(request.user)
        is_in_cart = services.is_product_in_cart(cart, product)

    product_url = request.build_absolute_uri(
        product.get_absolute_url()
    )

    description = clean_description(product.description)

    images = []

    if product.image:
        images.append(
            request.build_absolute_uri(product.image.url)
        )

    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "@id": f"{product_url}#product",
        "name": product.title,
        "description": description,
        "category": product.get_category_display(),
        "url": product_url,
        "sku": str(product.pk),
        "offers": product_offer(product, request),
    }

    if images:
        schema["image"] = images

    context = {
        "product": product,
        "is_in_cart": is_in_cart,
    }

    context.update(
        seo_context(
            request,
            title=f"{product.title} | بازارچه سینوالند",
            description=description,
            image=product.image,
            schema=schema,
            canonical_url=product_url,
            og_type="product",
        )
    )

    return render(
        request,
        "marketplace/detail.html",
        context,
    )
