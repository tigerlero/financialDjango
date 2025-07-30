from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.db.models import Sum, F
from django.utils import timezone


class Account(models.Model):
    """Bank account model with proper financial constraints"""
    ACCOUNT_TYPES = [
        ('checking', 'Checking'),
        ('savings', 'Savings'),
        ('credit', 'Credit Card'),
        ('investment', 'Investment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Current account balance"
    )
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'account_number']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.account_number})"
    
    def get_balance(self):
        return self.balance
    
    def can_debit(self, amount):
        """Check if account can be debited for the amount"""
        current_balance = self.get_balance()
        if self.account_type == 'credit':
            # For credit accounts, we might have a credit limit
            return True  # Simplified for demo
        return current_balance >= amount
    
    def get_transaction_count(self):
        """Get count of completed transactions"""
        return self.transactions.filter(status='completed').count()
    
    def save(self, *args, **kwargs):
        # Generate account number if not provided
        if not self.account_number:
            import uuid
            self.account_number = f"ACC{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)


class Category(models.Model):
    """Transaction categories for budgeting and reporting"""
    name = models.CharField(max_length=50)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='subcategories'
    )
    color = models.CharField(max_length=7, default='#007bff')  # Hex color
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Transaction(models.Model):
    """Core transaction model with financial integrity"""
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('transfer', 'Transfer'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Core fields
    account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference_number = models.CharField(max_length=50, unique=True)
    
    # Related account for transfers
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='incoming_transfers'
    )
    
    # External payment integration
    external_payment_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    transaction_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['account', 'transaction_date']),
            models.Index(fields=['status', 'transaction_date']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type.title()} ${self.amount} - {self.description}"
    
    def save(self, *args, **kwargs):
        # Generate reference number if not provided
        if not self.reference_number:
            import uuid
            self.reference_number = f"TXN{uuid.uuid4().hex[:8].upper()}"
        
        super().save(*args, **kwargs)
    
    def complete_transaction(self):
        """Mark transaction as completed and update account balance"""
        if self.status == 'completed':
            return
        
        # Update account balance
        if self.transaction_type == 'credit':
            self.account.balance += self.amount
        elif self.transaction_type == 'debit':
            if not self.account.can_debit(self.amount):
                raise ValueError("Insufficient funds")
            self.account.balance -= self.amount
        elif self.transaction_type == 'transfer' and self.to_account:
            self.account.balance -= self.amount
            self.to_account.balance += self.amount
            self.to_account.save()
        
        self.status = 'completed'
        self.account.save()
        self.save()


class RecurringTransaction(models.Model):
    """Model for recurring transactions like subscriptions"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    next_transaction_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Recurring: {self.description} - ${self.amount} {self.frequency}"


class PaymentMethod(models.Model):
    """Store payment method information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stripe_payment_method_id = models.CharField(max_length=100)
    card_last_four = models.CharField(max_length=4)
    card_brand = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.card_brand} ending in {self.card_last_four}"


class UserPreferences(models.Model):
    """Store user preferences and settings"""
    CURRENCY_CHOICES = [
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('GBP', 'GBP (£)'),
    ]
    
    DATE_FORMAT_CHOICES = [
        ('MM/DD/YYYY', 'MM/DD/YYYY'),
        ('DD/MM/YYYY', 'DD/MM/YYYY'),
        ('YYYY-MM-DD', 'YYYY-MM-DD'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light Theme'),
        ('dark', 'Dark Theme'),
        ('auto', 'Auto (System)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    default_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    date_format = models.CharField(max_length=20, choices=DATE_FORMAT_CHOICES, default='MM/DD/YYYY')
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    email_notifications = models.BooleanField(default=True)
    low_balance_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create preferences for a user"""
        try:
            preferences, created = cls.objects.get_or_create(
                user=user,
                defaults={
                    'default_currency': 'USD',
                    'date_format': 'MM/DD/YYYY',
                    'language': 'en',
                    'theme': 'light',
                    'email_notifications': True,
                    'low_balance_alerts': True,
                }
            )
            return preferences
        except Exception as e:
            # If there's an issue with the database, create a default preferences object
            # This is a fallback for cases where the migration hasn't been applied
            from django.core.exceptions import FieldDoesNotExist
            if 'theme' in str(e) or 'does not exist' in str(e):
                # Try to get existing preferences without the theme field
                try:
                    preferences = cls.objects.get(user=user)
                    return preferences
                except cls.DoesNotExist:
                    # Create a new preferences object with defaults
                    preferences = cls(
                        user=user,
                        default_currency='USD',
                        date_format='MM/DD/YYYY',
                        language='en',
                        email_notifications=True,
                        low_balance_alerts=True,
                    )
                    # Only set theme if the field exists
                    if hasattr(preferences, 'theme'):
                        preferences.theme = 'light'
                    preferences.save()
                    return preferences
            else:
                raise e
