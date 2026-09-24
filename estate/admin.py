from django.contrib import admin
from .models import Estate, EstateImage


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ['title', 'destination', 'get_reservation_count', 'duration', 'price', 'start_date', 'capacity',
                    'is_available']
    list_filter = ['duration', 'is_available', 'start_date']
    search_fields = ['title', 'get_reservation_count', 'destination', 'description']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_available']
    date_hierarchy = 'start_date'
    filter_horizontal = ['reserved_by']

    def get_reservation_count(self, obj):
        return obj.reserved_by.count()

    get_reservation_count.short_description = 'تعداد رزرو'


admin.site.unregister(Estate)  # If already registered
admin.site.register(Estate, EstateAdmin)


@admin.register(EstateImage)
class EstateImageAdmin(admin.ModelAdmin):
    list_display = ['estate', 'image', 'created_at']
    list_filter = ['created_at']
