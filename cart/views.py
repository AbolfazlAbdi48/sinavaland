import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.utils import IntegrityError
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from marketplace.models import Product
from .models import Cart, CartItem

from . import services


@login_required
def cart_detail(request):
    cart = services.get_cart(request.user)
    cart_items = cart.items.select_related('product') if cart else []

    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'cart_has_items': bool(cart_items),
    })


@login_required
@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    raw_quantity = request.POST.get('quantity', '1')

    try:
        quantity = int(raw_quantity)
        product_id = int(product_id)

        if quantity <= 0:
            raise ValueError

    except (TypeError, ValueError):
        messages.error(request, 'لطفاً شناسه محصول و تعداد معتبر وارد کنید.')
        return redirect('marketplace:list')

    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True
    )

    if quantity > product.stock:
        messages.error(request, 'تعداد درخواستی بیشتر از موجودی محصول است.')
        return redirect('marketplace:detail', slug=product.slug)

    cart = services.get_or_create_cart(request.user)

    try:
        services.add_product_to_cart(cart, product, quantity)
    except IntegrityError:
        messages.error(request, 'این محصول در سبد خرید شما موجود است.')
        return redirect('marketplace:detail', slug=product.slug)

    messages.success(request, "این محصول به سبد خرید شما اضافه شد.")
    return redirect('marketplace:detail', slug=product.slug)


@login_required
@require_POST
@transaction.atomic
def edit_cart(request):
    try:
        cart_data = json.loads(request.POST.get('cart_data', ''))
    except (json.JSONDecodeError, TypeError):
        messages.error(request, 'اطلاعات سبد خرید معتبر نیست.')
        return redirect('cart:cart-detail')

    if not isinstance(cart_data, list) or not cart_data:
        messages.error(request, 'اطلاعات سبد خرید معتبر نیست.')
        return redirect('cart:cart-detail')

    cart = services.get_cart(request.user)

    if cart is None:
        messages.error(request, 'سبد خرید شما خالی است.')
        return redirect('cart:cart-detail')

    validated_items = []
    seen_item_ids = set()

    try:
        for data in cart_data:
            if not isinstance(data, dict):
                raise ValueError

            item_id = data['item_id']
            quantity = data['quantity']

            if (
                    isinstance(item_id, bool)
                    or isinstance(quantity, bool)
                    or not isinstance(item_id, int)
                    or not isinstance(quantity, int)
            ):
                raise ValueError

            if item_id < 1 or quantity < 1:
                raise ValueError

            if item_id in seen_item_ids:
                raise ValueError

            seen_item_ids.add(item_id)

            item = cart.items.select_related('product').filter(pk=item_id).first()

            if item is None:
                messages.error(
                    request,
                    'یکی از آیتم‌های ارسالی در سبد خرید شما یافت نشد.'
                )
                return redirect('cart:cart-detail')

            if quantity > item.product.stock:
                messages.error(
                    request,
                    f'تعداد درخواستی محصول «{item.product.title}» '
                    'بیشتر از موجودی محصول است.'
                )
                return redirect('cart:cart-detail')

            validated_items.append((item, quantity))

    except (KeyError, TypeError, ValueError):
        messages.error(
            request,
            'لطفاً شناسه محصولات و تعدادهای معتبر ارسال کنید.'
        )
        return redirect('cart:cart-detail')

    with transaction.atomic():
        for item, quantity in validated_items:
            item.quantity = quantity
            item.save(update_fields=['quantity', 'updated_at'])

    messages.success(request, 'سبد خرید شما به‌روزرسانی شد.')
    return redirect('cart:cart-detail')


@login_required
@require_POST
def remove_cart_item(request, item_id):
    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart__user=request.user,
        cart__status=Cart.Status.ACTIVE
    )

    item.delete()

    messages.success(request, 'محصول از سبد خرید حذف شد.')
    return redirect('cart:cart-detail')
