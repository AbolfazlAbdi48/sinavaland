from django.contrib import admin
from .models import Estate, EstateImage


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'area', 'construction_year', 'rooms', 'is_available', 'is_vip',
                    'total_price']
    list_filter = ['is_available', 'is_vip', 'has_pool', 'has_parking', 'has_storage']
    search_fields = ['title', 'destination', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_available']


admin.site.unregister(Estate)  # If already registered
admin.site.register(Estate, EstateAdmin)


@admin.register(EstateImage)
class EstateImageAdmin(admin.ModelAdmin):
    list_display = ['estate', 'image', 'created_at']
    list_filter = ['created_at']
