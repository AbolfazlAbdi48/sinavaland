from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import Product
from cart import services


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
    product = get_object_or_404(Product, slug=slug, is_available=True)
    is_in_cart = False

    if request.user.is_authenticated:
        cart = services.get_cart(request.user)
        is_in_cart = services.is_product_in_cart(cart, product)

    return render(
        request,
        "marketplace/detail.html",
        {
            "product": product,
            "is_in_cart": is_in_cart,
        },
    )
