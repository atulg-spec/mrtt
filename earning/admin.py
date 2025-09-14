from django.contrib import admin
from .models import Wallet, LevelReward, UserLevelReward, WithdrawalMethod, WithdrawalRequest, UserBankAccount, UserUPIAccount


# -------------------------
# Wallet Admin
# -------------------------
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "balance",
        "locked_balance",
        "min_withdraw_limit",
    )
    list_filter = ("min_withdraw_limit",)
    search_fields = ("user__username", "user__email", "user__phone_number")
    readonly_fields = ("balance", "locked_balance")

    fieldsets = (
        ("User Information", {
            "fields": ("user",)
        }),
        ("Wallet Balances", {
            "fields": ("balance", "locked_balance"),
            "classes": ("collapse",),
        }),
        ("Settings", {
            "fields": ("min_withdraw_limit",),
        }),
    )

    def has_add_permission(self, request):
        # Prevent creating wallets manually from admin
        return False


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


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'method', 'status', 'created_at', 'transaction_id']
    list_filter = ['method', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'transaction_id']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    actions = ['mark_processing', 'mark_completed', 'mark_rejected']
    
    def mark_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_processing.short_description = "Mark selected as Processing"
    
    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Mark selected as Completed"
    
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_rejected.short_description = "Mark selected as Rejected"