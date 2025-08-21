from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, SelfieWithTree

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



@admin.register(SelfieWithTree)
class SelfieWithTreeAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "user",
        "uploaded_at",
        "is_verified",
    )
    list_filter = ("is_verified", "uploaded_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("preview", "uploaded_at")
    actions = ["mark_as_verified"]

    def thumbnail(self, obj):
        """Small image preview for list view"""
        if obj.selfie_image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px; object-fit:cover;" />',
                obj.selfie_image.url,
            )
        return "No Image"
    thumbnail.short_description = "Selfie"

    def preview(self, obj):
        """Larger image preview inside detail view"""
        if obj.selfie_image:
            return format_html(
                '<img src="{}" width="250" style="border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,0.15);" />',
                obj.selfie_image.url,
            )
        return "No Image"
    preview.short_description = "Selfie Preview"

    @admin.action(description="Mark selected selfies as verified ✅")
    def mark_as_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} selfies marked as verified ✅")

