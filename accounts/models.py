from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


class User(AbstractUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_golden = models.BooleanField(default=False, verbose_name='اشتراک طلایی')
    golden_expiry = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضای طلایی')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        return self.username


class OTP(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='otps'
    )
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = 'کد تایید'
        verbose_name_plural = 'کد های تایید'

    def __str__(self):
        return self.user.phone_number
