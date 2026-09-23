from django.db import models
from django.utils.text import slugify
from django.conf import settings

class Estate(models.Model):
    DURATION_CHOICES = [
        ('1day', 'یک روزه'),
        ('2day', 'دو روزه'),
        ('3day', 'سه روزه'),
        ('week', 'یک هفته'),
    ]

    title           = models.CharField(max_length=200, verbose_name='عنوان')
    slug            = models.SlugField(unique=True, allow_unicode=True)
    destination     = models.CharField(max_length=200, verbose_name='مقصد')
    duration        = models.CharField(max_length=20, choices=DURATION_CHOICES, verbose_name='مدت')
    description     = models.TextField(verbose_name='توضیحات')
    itinerary       = models.TextField(blank=True, verbose_name='برنامه سفر')
    included_services  = models.TextField(blank=True, verbose_name='خدمات شامل شده')
    excluded_services  = models.TextField(blank=True, verbose_name='خدمات شامل نشده')
    price           = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='قیمت')
    capacity        = models.PositiveIntegerField(verbose_name='ظرفیت')
    start_date      = models.DateField(verbose_name='تاریخ شروع')
    end_date        = models.DateField(verbose_name='تاریخ پایان', blank=True, null=True)
    image           = models.ImageField(upload_to='estate/', blank=True, null=True)
    is_available    = models.BooleanField(default=True, verbose_name='موجود')
    reserved_by     = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='reserved_estate',
        verbose_name='رزرو شده توسط'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ملک'
        verbose_name_plural = 'املاک'
        ordering = ['start_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def available_seats(self):
        return self.capacity - self.reserved_by.count()
