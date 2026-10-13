from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Product


def product_list(request):
    """لیست محصولات"""
    products = Product.objects.filter(is_available=True, stock__gt=0).order_by('-created_at')

    # فیلتر بر اساس دسته‌بندی
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    # جستجو
    search = request.GET.get('search')
    if search:
        products = products.filter(title__icontains=search) | products.filter(description__icontains=search)

    # صفحه‌بندی
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'marketplace/list.html', {
        'products': products,
        'categories': Product.CATEGORY_CHOICES
    })


def product_detail(request, slug):
    print("=== PERSIAN SLUG DEBUG ===")
    print("REQUEST PATH:", repr(request.path))
    print("PATH INFO:", repr(request.path_info))
    print("SCRIPT NAME:", repr(request.META.get("SCRIPT_NAME")))
    print("SCRIPT URL:", repr(request.META.get("SCRIPT_URL")))
    print("REDIRECT URL:", repr(request.META.get("REDIRECT_URL")))
    print("RAW PATH INFO:", repr(request.META.get("PATH_INFO")))
    print("RECEIVED SLUG:", repr(slug))

    product = get_object_or_404(
        Product,
        slug=slug,
        is_available=True,
    )
    return render(
        request,
        "marketplace/detail.html",
        {"product": product},
    )
