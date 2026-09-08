from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
from django.urls import reverse
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'phone_number', 'get_reservation_count', 'is_golden', 'golden_expiry']
    list_filter = ['is_golden', 'is_staff', 'is_superuser']
    search_fields = ['username', 'phone_number']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('phone_number',)}),
        ('Golden membership', {'fields': ('is_golden', 'golden_expiry')}),
        ('Reservations', {'fields': ('get_reservations_list',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ['get_reservations_list']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone_number', 'password1', 'password2'),
        }),
    )

    def get_reservation_count(self, obj):
        tours = obj.reserved_tours.count()
        accommodations = obj.reserved_accommodations.count()
        total = tours + accommodations
        return f"{total} ({tours}T + {accommodations}A)"

    get_reservation_count.short_description = 'Reservations'

    def get_reservations_list(self, obj):
        tours = obj.reserved_tours.all()
        accommodations = obj.reserved_accommodations.all()

        html = "<strong>Tours:</strong><br>"
        if tours:
            html += "<ul>"
            for tour in tours:
                url = reverse('admin:tours_tour_change', args=[tour.pk])
                html += f'<li><a href="{url}">{tour.title}</a></li>'
            html += "</ul>"
        else:
            html += "None<br>"

        html += "<br><strong>Accommodations:</strong><br>"
        if accommodations:
            html += "<ul>"
            for acc in accommodations:
                url = reverse('admin:accommodations_accommodation_change', args=[acc.pk])
                html += f'<li><a href="{url}">{acc.title}</a></li>'
            html += "</ul>"
        else:
            html += "None"

        return mark_safe(html)

    get_reservations_list.short_description = 'Reserved Items'


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'is_used', 'expires_at']
    list_filter = ['is_used']
    search_fields = ['user__phone_number']

    ordering = ('-created_at',)
