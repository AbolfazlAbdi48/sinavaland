from django.db import models
from accounts.models import phone_validator


class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام')
    subject = models.CharField(max_length=64, verbose_name='موضوع', null=True)
    email = models.EmailField(verbose_name='ایمیل')
    contact_number = models.CharField(max_length=15, verbose_name='شماره تماس', validators=[phone_validator], null=True)
    phone = models.CharField(max_length=15, verbose_name='موبایل', validators=[phone_validator])
    message = models.TextField(verbose_name='پیام')
    address = models.TextField(verbose_name='آدرس', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.created_at.strftime("%Y-%m-%d")}'
