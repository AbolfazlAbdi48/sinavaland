from django.db import models
from django.utils.text import slugify
from django.urls import reverse

from django_ckeditor_5.fields import CKEditor5Field
from imagekit.models import ImageSpecField

from core.image_specs import (
    ThumbnailSpec,
    CardImageSpec,
    LargeImageSpec,
    HomeCardLargeSpec,
)


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('food', 'خوراکی'),
        ('handicraft', 'صنایع دستی'),
        ('souvenir', 'سوغات'),
        ('other', 'سایر'),
    ]

    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, allow_unicode=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='دسته‌بندی')
    description = CKEditor5Field(
        config_name='default',
        blank=True,
        verbose_name='توضیحات'
    )
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='قیمت')
    stock = models.PositiveIntegerField(default=0, verbose_name='موجودی')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    thumbnail = ImageSpecField(
        source="image",
        spec=ThumbnailSpec,
    )
    card_image = ImageSpecField(
        source="image",
        spec=CardImageSpec,
    )
    large_image = ImageSpecField(
        source="image",
        spec=LargeImageSpec,
    )
    home_large_image = ImageSpecField(
        source="image",
        spec=HomeCardLargeSpec,
    )
    is_available = models.BooleanField(default=True, verbose_name='موجود')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'marketplace:detail',
            kwargs={'slug': self.slug}
        )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
