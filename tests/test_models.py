"""
Unit tests for models
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from transactions.models import Account, Transaction, Category, RecurringTransaction


@pytest.mark.unit
class TestAccountModel:
    """Test Account model"""
    
    def test_account_creation(self, user):
        """Test account creation"""
        account = Account.objects.create(
            user=user,
            name='Test Account',
            account_type='checking',
            account_number='ACC123',
            balance=Decimal('100.00')
        )
        
        assert account.name == 'Test Account'
        assert account.account_type == 'checking'
        assert account.balance == Decimal('100.00')
        assert account.currency == 'USD'
        assert account.is_active is True
        assert str(account) == 'Test Account (ACC123)'
    
    def test_account_unique_constraint(self, user):
        """Test unique constraint on account number per user"""
        Account.objects.create(
            user=user,
            name='Account 1',
            account_type='checking',
            account_number='ACC123'
        )
        
        with pytest.raises(IntegrityError):
            Account.objects.create(
                user=user,
                name='Account 2',
                account_type='savings',
                account_number='ACC123'
            )
    
    def test_get_balance_calculation(self, account):
        """Test balance calculation from transactions"""
        # Create transactions
        Transaction.objects.create(
            account=account,
            amount=Decimal('200.00'),
            description='Credit',
            transaction_type='credit',
            status='completed'
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Debit',
            transaction_type='debit',
            status='completed'
        )
        
        # Ignore pending transactions
        Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Pending',
            transaction_type='debit',
            status='pending'
        )
        
        calculated_balance = account.get_balance()
        assert calculated_balance == Decimal('150.00')  # 200 - 50
    
    def test_can_debit_checking_account(self, account):
        """Test debit validation for checking account"""
        account.account_type = 'checking'
        account.save()
        
        # Set up balance through transactions
        Transaction.objects.create(
            account=account,
            amount=Decimal('1000.00'),
            description='Initial balance',
            transaction_type='credit',
            status='completed'
        )
        
        # Should be able to debit within balance
        assert account.can_debit(Decimal('500.00')) is True
        
        # Should not be able to debit more than balance
        assert account.can_debit(Decimal('1500.00')) is False
    
    def test_can_debit_credit_account(self, account):
        """Test debit validation for credit account"""
        account.account_type = 'credit'
        account.save()
        
        # Credit accounts should allow debits (simplified logic)
        assert account.can_debit(Decimal('5000.00')) is True


@pytest.mark.unit
class TestTransactionModel:
    """Test Transaction model"""
    
    def test_transaction_creation(self, account, category):
        """Test transaction creation"""
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Test payment',
            transaction_type='debit',
            category=category
        )
        
        assert transaction.amount == Decimal('100.00')
        assert transaction.description == 'Test payment'
        assert transaction.transaction_type == 'debit'
        assert transaction.status == 'pending'
        assert transaction.category == category
        assert transaction.reference_number.startswith('TXN')
        assert len(transaction.reference_number) == 11  # TXN + 8 chars
    
    def test_transaction_string_representation(self, account):
        """Test transaction string representation"""
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('75.50'),
            description='Coffee shop',
            transaction_type='debit'
        )
        
        expected = 'Debit $75.50 - Coffee shop'
        assert str(transaction) == expected
    
    def test_complete_transaction_credit(self, account):
        """Test completing a credit transaction"""
        initial_balance = account.balance
        
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('200.00'),
            description='Salary',
            transaction_type='credit'
        )
        
        transaction.complete_transaction()
        
        account.refresh_from_db()
        assert account.balance == initial_balance + Decimal('200.00')
        assert transaction.status == 'completed'
    
    def test_complete_transaction_debit(self, account):
        """Test completing a debit transaction"""
        initial_balance = account.balance
        
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Groceries',
            transaction_type='debit'
        )
        
        transaction.complete_transaction()
        
        account.refresh_from_db()
        assert account.balance == initial_balance - Decimal('50.00')
        assert transaction.status == 'completed'
    
    def test_complete_transaction_insufficient_funds(self, account):
        """Test completing debit transaction with insufficient funds"""
        # Set account balance to a low amount
        account.balance = Decimal('10.00')
        account.save()
        
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Expensive item',
            transaction_type='debit'
        )
        
        with pytest.raises(ValueError, match='Insufficient funds'):
            transaction.complete_transaction()
    
    def test_complete_transfer_transaction(self, account, savings_account):
        """Test completing a transfer transaction"""
        initial_from_balance = account.balance
        initial_to_balance = savings_account.balance
        
        transaction = Transaction.objects.create(
            account=account,
            to_account=savings_account,
            amount=Decimal('300.00'),
            description='Transfer to savings',
            transaction_type='transfer'
        )
        
        transaction.complete_transaction()
        
        account.refresh_from_db()
        savings_account.refresh_from_db()
        
        assert account.balance == initial_from_balance - Decimal('300.00')
        assert savings_account.balance == initial_to_balance + Decimal('300.00')
        assert transaction.status == 'completed'
    
    def test_duplicate_completion_prevention(self, account):
        """Test that completing already completed transaction doesn't double-process"""
        initial_balance = account.balance
        
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Test',
            transaction_type='credit'
        )
        
        transaction.complete_transaction()
        first_completion_balance = account.balance
        
        # Try to complete again
        transaction.complete_transaction()
        
        account.refresh_from_db()
        assert account.balance == first_completion_balance


@pytest.mark.unit
class TestCategoryModel:
    """Test Category model"""
    
    def test_category_creation(self):
        """Test category creation"""
        category = Category.objects.create(
            name='Shopping',
            color='#007bff'
        )
        
        assert category.name == 'Shopping'
        assert category.color == '#007bff'
        assert category.is_active is True
        assert category.parent is None
        assert str(category) == 'Shopping'
    
    def test_category_hierarchy(self):
        """Test category parent-child relationship"""
        parent = Category.objects.create(name='Food', color='#28a745')
        child = Category.objects.create(
            name='Restaurants',
            parent=parent,
            color='#ffc107'
        )
        
        assert child.parent == parent
        assert child in parent.subcategories.all()
        assert str(child) == 'Food > Restaurants'


@pytest.mark.unit
class TestRecurringTransactionModel:
    """Test RecurringTransaction model"""
    
    def test_recurring_transaction_creation(self, account, category):
        """Test recurring transaction creation"""
        from django.utils import timezone
        
        next_date = timezone.now() + timezone.timedelta(days=30)
        
        recurring = RecurringTransaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Monthly subscription',
            category=category,
            frequency='monthly',
            next_transaction_date=next_date
        )
        
        assert recurring.amount == Decimal('50.00')
        assert recurring.frequency == 'monthly'
        assert recurring.is_active is True
        assert str(recurring) == 'Recurring: Monthly subscription - $50.00 monthly'
