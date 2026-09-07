from django.contrib import admin
from .models import Accommodation, AccommodationImage


@admin.register(Accommodation)
class AccommodationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'location', 'price_per_night', 'capacity', 'is_available',
                    'reserved_by']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['title', 'location', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(AccommodationImage)
class AccommodationImageAdmin(admin.ModelAdmin):
    list_display = ['accommodation', 'image', 'created_at']
    list_filter = ['created_at']
