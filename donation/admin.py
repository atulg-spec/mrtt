from django.contrib import admin
from .models import PaymentGateway, Payments, Donation, Registration_fee, ManualPayment
from django.utils import timezone

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
    list_display = ('id', 'user', 'amount', 'status', 'created_at', 'verified_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'transaction_id')
    readonly_fields = ('created_at',)
    actions = ['verify_payments', 'reject_payments']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'amount', 'transaction_id', 'status')
        }),
        ('Verification Details', {
            'fields': ('screenshot', 'notes', 'verified_at', 'verified_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if 'status' in form.changed_data and obj.status == 'VERIFIED':
            obj.verified_by = request.user
            print('working')
            payment = Payments.objects.create(user=obj.user,payment_method='MANUAL',razorpay_payment_id=obj.transaction_id,razorpay_order_id=obj.transaction_id,razorpay_signature=obj.transaction_id,amount_paid=obj.amount,status='Successful')
            if obj.user.registration_fee_paid:
                Donation.objects.create(user=obj.user, amount=payment.amount_paid)
            else:
                Registration_fee.objects.create(user=obj.user, amount=payment.amount_paid)

        super().save_model(request, obj, form, change)
    
    def verify_payments(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(
            status='VERIFIED',
            verified_at=timezone.now(),
            verified_by=request.user
        )
        self.message_user(request, f"{updated} payments verified successfully.")
    
    def reject_payments(self, request, queryset):
        updated = queryset.filter(status='PENDING').update(status='REJECTED')
        self.message_user(request, f"{updated} payments rejected.")
    
    verify_payments.short_description = "Verify selected payments"
    reject_payments.short_description = "Reject selected payments"