from django.contrib import admin
from .models import PaymentGateway, Payments, Donation, Registration_fee

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
    list_display = ('use', 'mode', 'razorpay_id_display')
    list_filter = ('use', 'mode')
    search_fields = ('razorpay_id',)

    def razorpay_id_display(self, obj):
        return obj.razorpay_id[:10] + '...' if len(obj.razorpay_id) > 10 else obj.razorpay_id
    razorpay_id_display.short_description = 'Razorpay ID'

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
