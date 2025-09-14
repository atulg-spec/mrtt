import uuid
from collections import deque
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from accounts.models import CustomUser

# -------------------------
# Wallet Model
# -------------------------
class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)   # Withdrawable
    locked_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)  # Not withdrawable yet
    min_withdraw_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    def deposit(self, amount, locked=False):
        if locked:
            self.locked_balance += amount
        else:
            self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount < self.min_withdraw_limit:
            return False, f"Minimum withdrawal limit is ₹{self.min_withdraw_limit}"
        if amount > self.balance:
            return False, "Insufficient balance"
        self.balance -= amount
        self.save()
        return True, "Withdrawal successful"

    def __str__(self):
        return f"{self.user.username} Wallet"


# -------------------------
# LevelReward Model
# -------------------------
class LevelReward(models.Model):
    level = models.IntegerField(unique=True)
    reward = models.DecimalField(max_digits=12, decimal_places=2)
    withdraw_allowed = models.BooleanField(default=False)  # Whether this level reward is withdrawable

    def __str__(self):
        return f"Level {self.level} → ₹{self.reward} ({'Withdraw' if self.withdraw_allowed else 'Locked'})"


class UserLevelReward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_level_rewards")
    level = models.IntegerField()
    reward = models.DecimalField(max_digits=12, decimal_places=2)
    given_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "level")  # prevent duplicate rewards

    def __str__(self):
        return f"{self.user.username} - Level {self.level} → ₹{self.reward}"


# -------------------------
# Auto create Wallet for each new user
# -------------------------
@receiver(post_save, sender=CustomUser)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


# -------------------------
# Withdrawal Models
# -------------------------
class WithdrawalMethod(models.Model):
    METHOD_CHOICES = (
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('paytm', 'PayTM'),
    )
    
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10, choices=METHOD_CHOICES, unique=True)
    is_active = models.BooleanField(default=True)
    processing_time = models.CharField(max_length=50, default="1-2 business days")
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=100.00)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=50000.00)
    icon = models.CharField(max_length=10, default="🏦")
    
    def __str__(self):
        return self.name


class UserBankAccount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bank_accounts")
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)
    bank_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.bank_name} ({self.account_number})"


class UserUPIAccount(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="upi_accounts")
    upi_id = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.upi_id}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    METHOD_CHOICES = (
        ('bank', 'Bank Transfer'),
        ('upi', 'UPI'),
        ('paytm', 'PayTM'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="withdrawals")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    
    # Bank transfer details
    bank_account = models.ForeignKey(UserBankAccount, on_delete=models.SET_NULL, null=True, blank=True)
    
    # UPI details
    upi_account = models.ForeignKey(UserUPIAccount, on_delete=models.SET_NULL, null=True, blank=True)
    
    # PayTM details
    paytm_mobile = models.CharField(max_length=15, blank=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=50, blank=True)
    admin_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"WD{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)



@receiver(post_save, sender=WithdrawalRequest)
def process_withdrawal(sender, instance, created, **kwargs):
    # If withdrawal is completed, deduct from wallet
    if instance.status == 'completed' and created:
        wallet = instance.user.wallet
        wallet.balance -= instance.amount
        wallet.save()