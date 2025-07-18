"""
Admin configuration for transactions app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Account, Transaction, Category, RecurringTransaction, PaymentMethod, UserPreferences


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'account_type', 'colored_balance', 'currency', 'is_active', 'transaction_count', 'created_at']
    list_filter = ['account_type', 'currency', 'is_active', 'created_at']
    search_fields = ['name', 'account_number', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'calculated_balance']
    list_per_page = 20
    actions = ['activate_accounts', 'deactivate_accounts']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'account_type', 'account_number')
        }),
        ('Financial Details', {
            'fields': ('balance', 'calculated_balance', 'currency', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_balance(self, obj):
        color = 'green' if obj.balance >= 0 else 'red'
        return format_html(
            '<span style="color: {};">${:,.2f}</span>',
            color, float(obj.balance)
        )
    colored_balance.short_description = 'Balance'
    
    def calculated_balance(self, obj):
        calculated = obj.get_balance()
        return format_html("${:,.2f}", float(calculated))
    calculated_balance.short_description = 'Calculated Balance'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def transaction_count(self, obj):
        return obj.get_transaction_count()
    transaction_count.short_description = 'Transactions'
    
    def activate_accounts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} accounts activated.')
    activate_accounts.short_description = 'Activate selected accounts'
    
    def deactivate_accounts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} accounts deactivated.')
    deactivate_accounts.short_description = 'Deactivate selected accounts'


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'reference_number', 'account', 'transaction_type', 'colored_amount', 
        'description', 'status_badge', 'transaction_date', 'account_user'
    ]
    list_filter = ['transaction_type', 'status', 'transaction_date', 'account__account_type', 'account__user']
    search_fields = ['reference_number', 'description', 'account__name', 'account__user__username']
    readonly_fields = ['reference_number', 'created_at', 'updated_at']
    date_hierarchy = 'transaction_date'
    list_per_page = 50
    actions = ['mark_as_completed', 'mark_as_failed']
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('reference_number', 'account', 'transaction_type', 'amount', 'description')
        }),
        ('Categorization', {
            'fields': ('category', 'to_account')
        }),
        ('Status & Payment', {
            'fields': ('status', 'external_payment_id', 'payment_method')
        }),
        ('Timestamps', {
            'fields': ('transaction_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def colored_amount(self, obj):
        color = 'green' if obj.transaction_type == 'credit' else 'red'
        symbol = '+' if obj.transaction_type == 'credit' else '-'
        return format_html(
            '<span style="color: {};">{} ${:,.2f}</span>',
            color, symbol, float(obj.amount)
        )
    colored_amount.short_description = 'Amount'
    
    def status_badge(self, obj):
        colors = {
            'completed': 'green',
            'pending': 'orange',
            'failed': 'red',
            'cancelled': 'gray'
        }
        color = colors.get(obj.status, 'blue')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px;">{}</span>',
            color, obj.status.title()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('account', 'category', 'to_account')
    
    def account_user(self, obj):
        return obj.account.user.username
    account_user.short_description = 'User'
    
    def mark_as_completed(self, request, queryset):
        updated = 0
        for transaction in queryset:
            if transaction.status != 'completed':
                transaction.status = 'completed'
                transaction.save()
                updated += 1
        self.message_user(request, f'{updated} transactions marked as completed.')
    mark_as_completed.short_description = 'Mark selected transactions as completed'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} transactions marked as failed.')
    mark_as_failed.short_description = 'Mark selected transactions as failed'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'color_preview', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    list_editable = ['is_active']
    
    def color_preview(self, obj):
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div> {}',
            obj.color, obj.color
        )
    color_preview.short_description = 'Color'


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'description', 'account', 'amount', 'frequency', 
        'next_transaction_date', 'is_active'
    ]
    list_filter = ['frequency', 'is_active']
    search_fields = ['description', 'account__name']
    date_hierarchy = 'next_transaction_date'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_brand', 'masked_card_number', 'is_default', 'created_at']
    list_filter = ['card_brand', 'is_default']
    search_fields = ['user__username', 'card_last_four']
    readonly_fields = ['created_at']
    
    def masked_card_number(self, obj):
        return f"**** **** **** {obj.card_last_four}"
    masked_card_number.short_description = 'Card Number'


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'default_currency', 'date_format', 'language', 'theme', 'email_notifications', 'low_balance_alerts']
    list_filter = ['default_currency', 'date_format', 'language', 'theme', 'email_notifications', 'low_balance_alerts']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Preferences', {
            'fields': ('default_currency', 'date_format', 'language', 'theme')
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'low_balance_alerts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Customize admin site
admin.site.site_header = "Finance App Administration"
admin.site.site_title = "Finance App Admin"
admin.site.index_title = "Welcome to Finance App Administration"
