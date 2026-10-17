from .models import Cart, CartItem


def get_or_create_cart(user):
    cart, created = Cart.objects.get_or_create(
        user=user,
        status=Cart.Status.ACTIVE
    )

    return cart


def get_cart(user):
    return Cart.objects.filter(
        user=user,
        status=Cart.Status.ACTIVE
    ).first()


def is_product_in_cart(cart, product):
    return CartItem.objects.filter(
        cart=cart,
        product=product
    ).exists()


def add_product_to_cart(cart, product, quantity):
    CartItem.objects.create(
        cart=cart,
        product=product,
        quantity=quantity
    )
