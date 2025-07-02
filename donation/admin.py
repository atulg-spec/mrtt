from django.contrib import admin
from .models import PaymentGateway, Payments, Donation

@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('use', 'mode', 'razorpay_id_display')
    list_filter = ('use', 'mode')
    search_fields = ('razorpay_id',)

    def razorpay_id_display(self, obj):
        return obj.razorpay_id[:10] + '...' if len(obj.razorpay_id) > 10 else obj.razorpay_id
    razorpay_id_display.short_description = 'Razorpay ID'

@admin.register(Payments)
class PaymentsAdmin(admin.ModelAdmin):
    list_display = ('razorpay_payment_id', 'user', 'payment_method', 'amount_paid', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
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
