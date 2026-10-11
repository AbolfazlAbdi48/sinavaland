from django.db import models
from django.utils.text import slugify
from accounts.models import User

from django_ckeditor_5.fields import CKEditor5Field

class Article(models.Model):
    CATEGORY_CHOICES = [
        ('travel', 'سفر'),
        ('culture', 'فرهنگ'),
        ('food', 'غذا'),
        ('nature', 'طبیعت'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(unique=True, allow_unicode=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='دسته‌بندی')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='نویسنده')
    content = CKEditor5Field(
        config_name='default',
        blank=True,
        verbose_name='محتوا'
    )
    excerpt = models.TextField(max_length=300, verbose_name='خلاصه')
    image = models.ImageField(upload_to='article/', blank=True, null=True)
    is_published = models.BooleanField(default=False, verbose_name='منتشر شده')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)
