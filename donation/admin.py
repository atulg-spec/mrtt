from django.contrib import admin
from .models import PaymentGateway, Payments, Donation, Registration_fee, ManualPayment
from django.utils import timezone
from django.utils.html import format_html

@admin.register(Registration_fee)
class RegistrationFeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'time']
    list_filter = ['time']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

    def save_model(self, request, obj, form, change):
        if not obj.user.registration_fee_paid:
            obj.user.registration_fee_paid = True
            obj.user.amount_paid = obj.amount
            obj.user.save()
        super().save_model(request, obj, form, change)

    def __str__(self):
        return f'{self.user.first_name} paid {self.amount}'


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('id', 'use', 'mode')
    list_filter = ('use', 'mode')
    search_fields = ('use', 'mode')
    readonly_fields = ('id',)

    fieldsets = (
        (None, {
            'fields': ('use', ('razorpay_id', 'razorpay_secret'), ('payment_qr', 'payment_upi_id'), 'mode')
        }),
        ('Additional Information', {
            'fields': ('id',),
            'classes': ('collapse',),
        }),
    )

    def __str__(self):
        return "Payment Settings"


@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('razorpay_payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('payment_method', 'user', 'status', 'created_at')
    search_fields = ('razorpay_payment_id', 'user__username', 'user__email')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'time')
    list_filter = ('time',)
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'time'
    ordering = ('-time',)


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'created_at', 'verified_at', 'screenshot_tag')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at', 'screenshot_preview')
    actions = ['verify_payments', 'reject_payments']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'transaction_id', 'status', 'screenshot', 'screenshot_preview', 'notes', 'verified_at', 'verified_by')
        }),
        # ('Verification Details', {
        #     'fields': ('screenshot', 'screenshot_preview', 'notes', 'verified_at', 'verified_by'),
        #     'classes': ('collapse',)
        # }),
    )

    def screenshot_tag(self, obj):
        """Show thumbnail in list display"""
        if obj.screenshot:
            return format_html(
                '<img src="{}" style="height: 50px; width: auto; border-radius: 4px; box-shadow: 0 0 4px rgba(0,0,0,0.3);" />',
                obj.screenshot.url
            )
        return "No Image"
    screenshot_tag.short_description = "Screenshot"

    def screenshot_preview(self, obj):
        """Show bigger preview in detail view"""
        if obj.screenshot:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="max-height: 300px; max-width: 100%; '
                'border: 1px solid #ddd; border-radius: 6px; padding: 4px; background: #f9f9f9;" />'
                '</a>',
                obj.screenshot.url
            )
        return "No Image Uploaded"
    screenshot_preview.short_description = "Screenshot Preview"
    
    def verify_payments(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(
            status='VERIFIED',
            verified_at=timezone.now(),
            verified_by=request.user
        )
        for x in queryset:
            payment = Payments.objects.create(
                user=x.user,
                payment_method='MANUAL',
                razorpay_payment_id=x.transaction_id,
                razorpay_order_id=x.transaction_id,
                razorpay_signature=x.transaction_id,
                amount_paid=x.amount,
                status='Successful'
            )
            if x.user.registration_fee_paid:
                Donation.objects.create(user=x.user, amount=payment.amount_paid)
            else:
                try:
                    Registration_fee.objects.create(user=x.user, amount=payment.amount_paid)
                except:
                    pass
        self.message_user(request, f"{updated} payments verified successfully.")
    
    def reject_payments(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f"{updated} payments rejected.")
    
    verify_payments.short_description = "Verify selected payments"
    reject_payments.short_description = "Reject selected payments"