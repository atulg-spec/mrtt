from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, SelfieWithTree
from earning.utils import get_paid_downline, get_level

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'phone_number', 'is_staff', 'date_joined', 'registration_fee_paid', 'amount_paid' , 'team_total', 'user_level')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'referred_by', 'registration_fee_paid')

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

    def team_total(self, obj):
        return len(get_paid_downline(obj))
    team_total.short_description = "Team Members"

    def user_level(self, obj):
        return get_level(len(get_paid_downline(obj)))
    user_level.short_description = "Level"


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



@admin.register(SelfieWithTree)
class SelfieWithTreeAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "uploaded_at", "selfie_preview")
    list_filter = ("status",)
    search_fields = ("user__username",)

    def selfie_preview(self, obj):
        if obj.selfie_image:
            return format_html('<img src="{}" width="80" height="80" style="border-radius:8px;object-fit:cover;" />', obj.selfie_image.url)
        return "No Image"

    selfie_preview.short_description = "Selfie"

    actions = ["mark_verified", "mark_rejected"]

    def mark_verified(self, request, queryset):
        queryset.update(status="verified", rejection_reason=None)
    mark_verified.short_description = "Mark selected selfies as Verified"

    def mark_rejected(self, request, queryset):
        queryset.update(status="rejected")
    mark_rejected.short_description = "Mark selected selfies as Rejected"
