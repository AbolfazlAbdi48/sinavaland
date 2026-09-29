from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings

from accounts.models import phone_validator


class Estate(models.Model):
    DURATION_CHOICES = [
        ('1day', 'یک روزه'),
        ('2day', 'دو روزه'),
        ('3day', 'سه روزه'),
        ('week', 'یک هفته'),
    ]

    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, allow_unicode=True)
    destination = models.CharField(max_length=200, verbose_name='مقصد')

    area = models.PositiveIntegerField(verbose_name='متراژ')
    construction_year = models.PositiveIntegerField(verbose_name='سال ساخت')
    rooms = models.PositiveSmallIntegerField(verbose_name='تعداد اتاق')
    floor = models.IntegerField(verbose_name='طبقه')

    has_pool = models.BooleanField(default=False, verbose_name='استخر')
    has_parking = models.BooleanField(default=False, verbose_name='پارکینگ')
    has_storage = models.BooleanField(default=False, verbose_name='انباری')

    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=0,
        verbose_name='قیمت کل'
    )

    description = models.TextField(verbose_name='توضیحات')
    is_available = models.BooleanField(default=True, verbose_name='موجود')
    is_vip = models.BooleanField(default=False, verbose_name='ویژه')
    owner_phone_number = models.CharField(max_length=11, verbose_name='شماره تماس مالک',
                                          validators=[phone_validator])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ملک'
        verbose_name_plural = 'املاک'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def price_per_meter(self):
        if self.area:
            return self.total_price / self.area
        return 0


class EstateImage(models.Model):
    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='estate/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'تصویر ملک'
        verbose_name_plural = 'تصاویر املاک'
        ordering = ['created_at']
