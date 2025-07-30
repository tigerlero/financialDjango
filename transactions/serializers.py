"""
DRF serializers for API endpoints
"""
from rest_framework import serializers
from .models import Account, Transaction, Category, RecurringTransaction, PaymentMethod


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'color', 'is_active']


class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""
    current_balance = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'account_type', 'account_number', 
            'balance', 'currency', 'is_active', 'created_at',
            'current_balance', 'transaction_count'
        ]
        read_only_fields = ['account_number', 'created_at']
    
    def get_current_balance(self, obj):
        return obj.get_balance()
    
    def create(self, validated_data):
        # Ensure balance is properly handled as Decimal
        balance = validated_data.get('balance', 0)  # default to 0 if balance is not present
        validated_data['balance'] = balance
        instance = super().create(validated_data)
        instance.save()
        return instance
    
    def get_transaction_count(self, obj):
        return obj.transactions.count()


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    account_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    to_account_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'account', 'account_name', 'transaction_type', 'amount',
            'description', 'category', 'category_name', 'status',
            'reference_number', 'to_account', 'to_account_name',
            'external_payment_id', 'payment_method', 'transaction_date',
            'created_at', 'metadata'
        ]
        read_only_fields = ['reference_number', 'created_at']
    
    def get_account_name(self, obj):
        return obj.account.name
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_to_account_name(self, obj):
        return obj.to_account.name if obj.to_account else None


class RecurringTransactionSerializer(serializers.ModelSerializer):
    """Serializer for RecurringTransaction model"""
    account_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    
    class Meta:
        model = RecurringTransaction
        fields = [
            'id', 'account', 'account_name', 'amount', 'description',
            'category', 'category_name', 'frequency', 'next_transaction_date',
            'is_active', 'created_at'
        ]
    
    def get_account_name(self, obj):
        return obj.account.name
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for PaymentMethod model"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'id', 'stripe_payment_method_id', 'card_last_four',
            'card_brand', 'is_default', 'created_at'
        ]
        read_only_fields = ['created_at']


class TransactionCreateSerializer(serializers.Serializer):
    """Serializer for transaction creation"""
    account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(max_length=255)
    transaction_type = serializers.ChoiceField(
        choices=[('credit', 'Credit'), ('debit', 'Debit')]
    )
    category_id = serializers.IntegerField(required=False)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class TransferSerializer(serializers.Serializer):
    """Serializer for fund transfers"""
    from_account_id = serializers.IntegerField()
    to_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(max_length=255)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate(self, data):
        if data['from_account_id'] == data['to_account_id']:
            raise serializers.ValidationError(
                "Cannot transfer to the same account"
            )
        return data


class PaymentSerializer(serializers.Serializer):
    """Serializer for payment processing"""
    account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(max_length=255)
    payment_method_id = serializers.CharField(max_length=100)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
