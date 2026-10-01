from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import mark_safe
from django.urls import reverse
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'first_name', 'last_name', 'get_reservation_count', 'is_golden', 'golden_expiry']
    list_filter = ['is_golden', 'is_staff', 'is_superuser']
    search_fields = ['first_name', 'last_name']

    fieldsets = (
        (None, {'fields': ('password',)}),
        ('Personal info', {'fields': ('username', 'first_name', 'last_name')}),
        ('Golden membership', {'fields': ('is_golden', 'golden_expiry')}),
        ('Reservations', {'fields': ('get_reservations_list',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    readonly_fields = ['get_reservations_list']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('password1', 'password2'),
        }),
    )

    def get_reservation_count(self, obj):
        accommodations = obj.reserved_accommodations.count()
        return f"{accommodations}A)"

    get_reservation_count.short_description = 'Reservations'

    def get_reservations_list(self, obj):
        accommodations = obj.reserved_accommodations.all()

        html = "<br><strong>Accommodations:</strong><br>"
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
