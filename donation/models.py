from django.db import models
from accounts.models import CustomUser as User
from django.utils import timezone

class PaymentGateway(models.Model):
    USE = (
        ('RAZORPAY', 'RAZORPAY'),
        ('MANUAL', 'MANUAL'),
    )

    use = models.CharField(choices=USE,max_length=10,default='RAZORPAY')
    razorpay_id = models.CharField(max_length=500,default="")
    razorpay_secret = models.CharField(max_length=500,default="")

    payment_qr = models.ImageField(upload_to='payment/', verbose_name="Payment QR", null=True, blank=True)
    payment_upi_id = models.CharField(max_length=255, blank=True, null=True, help_text="Enter your Payment UPI ID.")

    mode = models.CharField(max_length=10,help_text="LIVE or TEST")

    class Meta:
        verbose_name = "Payment Setting"
        verbose_name_plural = "Payment Settings"
    def __str__(self):
      return "Payment Settings"
    
    

class Payments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=200, default="")
    razorpay_order_id = models.CharField(max_length=200, default="")
    razorpay_signature = models.CharField(max_length=200, default="")
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return self.razorpay_payment_id


class Registration_fee(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registration Fee" 
        verbose_name_plural = "Registration Fees"

    def save(self, *args, **kwargs):
        if not self.user.registration_fee_paid:
            self.user.registration_fee_paid = True
            self.user.amount_paid = self.amount
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.first_name} paid {self.amount}'


class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Donation"
        verbose_name_plural = "Donations"

    def __str__(self):
        return f'{self.user.first_name} donated {self.amount}'
    

class ManualPayment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=200)
    screenshot = models.ImageField(upload_to='manual_payments/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True, 
        related_name='verified_manual_payments'
    )

    class Meta:
        verbose_name = "Manual Payment"
        verbose_name_plural = "Manual Payments"
        ordering = ['-created_at']

    def __str__(self):
        return f"Manual Payment #{self.id} - {self.user.username} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        # Update verified_at when status changes to VERIFIED
        if self.status == 'VERIFIED' and not self.verified_at:
            self.verified_at = timezone.now()
        super().save(*args, **kwargs)