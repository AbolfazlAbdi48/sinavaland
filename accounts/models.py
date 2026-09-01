from django.contrib.auth.models import AbstractUser
from django.db import models    

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_golden = models.BooleanField(default=False, verbose_name='اشتراک طلایی')
    golden_expiry = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ انقضای طلایی')
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    
    def __str__(self):
        return self.username
