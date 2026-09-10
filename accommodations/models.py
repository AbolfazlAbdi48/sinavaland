from django.db import models
from django.utils.text import slugify
from django.conf import settings
from .utils import generate_accommodation_code


class Accommodation(models.Model):
    CATEGORY_CHOICES = [
        ('hotel', 'هتل'),
        ('villa', 'ویلا'),
        ('apartment', 'آپارتمان'),
        ('ecolodge', 'بومگردی'),
    ]

    code = models.CharField(
        max_length=16,
        unique=True,
        blank=True,
        editable=False,
        verbose_name='کد اقامتگاه'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, allow_unicode=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='دسته‌بندی')
    description = models.TextField(verbose_name='توضیحات')
    location = models.CharField(max_length=200, verbose_name='موقعیت')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='قیمت هر شب')
    capacity = models.PositiveIntegerField(verbose_name='ظرفیت')
    is_available = models.BooleanField(default=True, verbose_name='موجود')
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='reserved_accommodations',
        verbose_name='رزرو شده توسط'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'اقامتگاه'
        verbose_name_plural = 'اقامتگاه‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)

        super().save(*args, **kwargs)

        if not self.code:
            self.code = generate_accommodation_code(self.pk)
            super().save(update_fields=['code'])

    # ── aliases so templates can use .name and .available ──
    @property
    def name(self):
        return self.title

    @property
    def available(self):
        return self.is_available


class AccommodationImage(models.Model):
    accommodation = models.ForeignKey(
        Accommodation,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='accommodations/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تصویر اقامتگاه'
        verbose_name_plural = 'تصاویر اقامتگاه‌ها'
        ordering = ['created_at']
