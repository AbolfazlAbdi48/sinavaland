from django.db import models
from django.conf import settings

from marketplace.models import Product


class Cart(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'فعال'
        COMPLETED = 'completed', 'تکمیل شده'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='کاربر'
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name='وضعیت'
    )

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'
        ordering = ['-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(status='active'),
                name='unique_active_cart_per_user',
            ),
        ]

    def __str__(self):
        return f"Cart #{self.pk} - {self.status}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='آیتم ها'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='cart_items',
        verbose_name='محصول',
    )

    quantity = models.PositiveIntegerField(verbose_name='تعداد')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        verbose_name = 'آیتم‌های سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        ordering = ['-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='unique_product_per_cart',
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name='cart_item_quantity_gte_1',
            ),
        ]

    def __str__(self):
        return f'{self.product} × {self.quantity}'
