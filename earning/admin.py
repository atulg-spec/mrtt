from django.contrib import admin, messages
from .models import Wallet, LevelReward, UserLevelReward, WithdrawalMethod, WithdrawalRequest, UserBankAccount, UserUPIAccount


# -------------------------
# Wallet Admin
# -------------------------
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "locked_balance", "min_withdraw_limit")
    list_filter = ("min_withdraw_limit",)
    search_fields = ("user__username", "user__email", "user__phone_number")

    fieldsets = (
        ("User Information", {
            "fields": ("user",)
        }),
        ("Wallet Balances", {
            "fields": ("balance", "locked_balance"),
        }),
        ("Settings", {
            "fields": ("min_withdraw_limit",),
        }),
    )

    def has_add_permission(self, request):
        # Prevent creating wallets manually from admin
        return False


# -------------------------
# WithdrawalRequest Admin
# -------------------------
@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "amount",
        "method",
        "status",
        "transaction_id",
        "wallet_balance",  # custom column
        "created_at",
    )
    list_filter = ("status", "method", "created_at")
    search_fields = ("user__username", "user__email", "transaction_id")
    actions = ["mark_as_completed", "mark_as_rejected"]

    def wallet_balance(self, obj):
        """Show the user's current wallet balance"""
        return f"₹{obj.user.wallet.balance}"
    wallet_balance.short_description = "Wallet Balance"

    def mark_as_completed(self, request, queryset):
        """Admin action to complete withdrawals and deduct from wallet"""
        updated = 0
        for withdrawal in queryset.filter(status="pending"):
            wallet = withdrawal.user.wallet
            if withdrawal.amount > wallet.balance:
                self.message_user(
                    request,
                    f"Insufficient balance in {withdrawal.user.username}'s wallet "
                    f"for withdrawal ₹{withdrawal.amount}.",
                    level=messages.ERROR,
                )
                continue

            # Deduct balance
            wallet.balance -= withdrawal.amount
            wallet.save()

            # Update withdrawal status
            withdrawal.status = "completed"
            withdrawal.save()

            updated += 1

        self.message_user(request, f"{updated} withdrawal(s) marked as completed.")

    mark_as_completed.short_description = "Mark selected withdrawals as Completed"

    def mark_as_rejected(self, request, queryset):
        """Admin action to reject withdrawals (no wallet changes)"""
        updated = queryset.filter(status="pending").update(status="rejected")
        self.message_user(request, f"{updated} withdrawal(s) rejected.")

    mark_as_rejected.short_description = "Reject selected withdrawals"


@admin.register(UserLevelReward)
class UserLevelRewardAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "level", "reward", "given_at")   # Columns in list view
    list_filter = ("level", "given_at")                           # Side filters
    search_fields = ("user__username", "user__email")             # Search by username/email
    ordering = ("-given_at",)                                     # Latest first
    readonly_fields = ("given_at",)                               # Prevent editing
    list_per_page = 25                                            # Pagination

    fieldsets = (
        ("User & Level", {
            "fields": ("user", "level"),
            "description": "Assign the reward to a specific user and level."
        }),
        ("Reward Details", {
            "fields": ("reward", "given_at"),
            "description": "Reward amount and timestamp."
        }),
    )


# -------------------------
# Level Reward Admin
# -------------------------
@admin.register(LevelReward)
class LevelRewardAdmin(admin.ModelAdmin):
    list_display = ("level", "reward", "withdraw_allowed")
    list_editable = ("reward", "withdraw_allowed")
    ordering = ("level",)
    search_fields = ("level",)
    list_filter = ("withdraw_allowed",)

    fieldsets = (
        ("Reward Details", {
            "fields": ("level", "reward", "withdraw_allowed"),
        }),
    )


@admin.register(WithdrawalMethod)
class WithdrawalMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'min_amount', 'max_amount', 'processing_time']
    list_editable = ['is_active', 'min_amount', 'max_amount']


@admin.register(UserBankAccount)
class UserBankAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'bank_name', 'account_holder_name', 'account_number', 'is_primary', 'created_at']
    list_filter = ['bank_name', 'is_primary', 'created_at']
    search_fields = ['user__username', 'user__email', 'account_holder_name', 'account_number']


@admin.register(UserUPIAccount)
class UserUPIAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'upi_id', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['user__username', 'user__email', 'upi_id']
