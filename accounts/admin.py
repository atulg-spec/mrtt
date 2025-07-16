from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'is_staff', 'date_joined', 'registration_fee_paid', 'amount_paid')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'referred_by')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {
            'fields': (
                'first_name', 'last_name', 'phone_number', 'profile_picture',
                'address_line_1', 'address_line_2', 'state', 'country',
                'region_name', 'city', 'zip_code', 'lat', 'lon',
                'timezone', 'isp', 'aadhaar_number', 'date_of_birth', 'pan_number',
            )
        }),
        ('Registration Info', {
            'fields': (
                'registration_fee_paid', 'amount_paid'
            )
        }),
        ('Invite Information', {
            'fields': ('referral_code', 'referred_by')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {'fields': ('last_login',)}),
    )

    readonly_fields = ('date_joined', 'last_login')  # Add date_joined here

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2',
                'is_staff', 'is_active'
            ),
        }),
    )

    search_fields = ('email', 'username')
    ordering = ('-date_joined',)

admin.site.register(CustomUser, CustomUserAdmin)
