"""
Unit tests for services
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.contrib.auth.models import User
from transactions.models import Account, Transaction, Category
from transactions.services import (
    StripePaymentService, TransactionService, AnalyticsService
)


@pytest.mark.unit
class TestStripePaymentService:
    """Test Stripe payment service"""
    
    @patch('transactions.services.stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_create):
        """Test successful payment intent creation"""
        mock_intent = MagicMock()
        mock_intent.id = 'pi_test_123'
        mock_intent.client_secret = 'pi_test_123_secret'
        mock_create.return_value = mock_intent
        
        result = StripePaymentService.create_payment_intent(
            amount=Decimal('100.00'),
            currency='usd',
            metadata={'test': 'data'}
        )
        
        assert result['success'] is True
        assert result['client_secret'] == 'pi_test_123_secret'
        assert result['payment_intent_id'] == 'pi_test_123'
        
        mock_create.assert_called_once_with(
            amount=10000,  # $100.00 in cents
            currency='usd',
            metadata={'test': 'data'}
        )
    
    @patch('transactions.services.stripe.PaymentIntent.create')
    def test_create_payment_intent_failure(self, mock_create):
        """Test payment intent creation failure"""
        import stripe
        mock_create.side_effect = stripe.error.StripeError("Card declined")
        
        result = StripePaymentService.create_payment_intent(
            amount=Decimal('100.00')
        )
        
        assert result['success'] is False
        assert 'Card declined' in result['error']
    
    @patch('transactions.services.stripe.PaymentIntent.retrieve')
    def test_confirm_payment_success(self, mock_retrieve):
        """Test successful payment confirmation"""
        mock_intent = MagicMock()
        mock_intent.status = 'succeeded'
        mock_intent.payment_method = 'pm_test_123'
        mock_retrieve.return_value = mock_intent
        
        result = StripePaymentService.confirm_payment('pi_test_123')
        
        assert result['success'] is True
        assert result['status'] == 'succeeded'
        assert result['payment_method'] == 'pm_test_123'
    
    @patch('transactions.services.stripe.PaymentIntent.retrieve')
    def test_confirm_payment_failure(self, mock_retrieve):
        """Test payment confirmation failure"""
        mock_intent = MagicMock()
        mock_intent.status = 'requires_payment_method'
        mock_retrieve.return_value = mock_intent
        
        result = StripePaymentService.confirm_payment('pi_test_123')
        
        assert result['success'] is False
        assert result['status'] == 'requires_payment_method'
    
    @patch('transactions.services.stripe.Customer.create')
    def test_create_customer_success(self, mock_create):
        """Test successful customer creation"""
        mock_customer = MagicMock()
        mock_customer.id = 'cus_test_123'
        mock_create.return_value = mock_customer
        
        result = StripePaymentService.create_customer(
            user_id=1,
            email='test@example.com'
        )
        
        assert result['success'] is True
        assert result['customer_id'] == 'cus_test_123'
        
        mock_create.assert_called_once_with(
            email='test@example.com',
            metadata={'user_id': 1}
        )


@pytest.mark.unit
class TestTransactionService:
    """Test transaction service"""
    
    def test_create_transaction_success(self, account, category):
        """Test successful transaction creation"""
        transaction = TransactionService.create_transaction(
            account=account,
            amount=Decimal('50.00'),
            description='Test purchase',
            transaction_type='debit',
            category=category,
            metadata={'test': 'data'}
        )
        
        assert transaction.account == account
        assert transaction.amount == Decimal('50.00')
        assert transaction.description == 'Test purchase'
        assert transaction.transaction_type == 'debit'
        assert transaction.category == category
        assert transaction.metadata == {'test': 'data'}
        assert transaction.status == 'pending'
    
    def test_create_transaction_insufficient_funds(self, account):
        """Test transaction creation with insufficient funds"""
        # Set account balance to 0
        account.balance = Decimal('0.00')
        account.save()
        
        with pytest.raises(ValueError, match='Insufficient funds'):
            TransactionService.create_transaction(
                account=account,
                amount=Decimal('100.00'),
                description='Expensive item',
                transaction_type='debit'
            )
    
    @patch('transactions.services.StripePaymentService.create_payment_intent')
    @patch('transactions.services.process_payment_async.delay')
    def test_process_payment_success(self, mock_delay, mock_create_intent, account):
        """Test successful payment processing"""
        mock_create_intent.return_value = {
            'success': True,
            'client_secret': 'pi_test_123_secret',
            'payment_intent_id': 'pi_test_123'
        }
        
        result = TransactionService.process_payment(
            account=account,
            amount=Decimal('75.00'),
            payment_method_id='pm_test_123',
            description='Online purchase'
        )
        
        assert result['success'] is True
        assert 'transaction_id' in result
        assert result['client_secret'] == 'pi_test_123_secret'
        
        # Verify transaction was created
        transaction = Transaction.objects.get(id=result['transaction_id'])
        assert transaction.amount == Decimal('75.00')
        assert transaction.description == 'Online purchase'
        assert transaction.status == 'pending'
        
        # Verify async task was called
        mock_delay.assert_called_once()
    
    @patch('transactions.services.StripePaymentService.create_payment_intent')
    def test_process_payment_stripe_failure(self, mock_create_intent, account):
        """Test payment processing with Stripe failure"""
        mock_create_intent.return_value = {
            'success': False,
            'error': 'Card declined'
        }
        
        result = TransactionService.process_payment(
            account=account,
            amount=Decimal('75.00'),
            payment_method_id='pm_test_123',
            description='Online purchase'
        )
        
        assert result['success'] is False
        assert result['error'] == 'Card declined'
    
    def test_transfer_funds_success(self, account, savings_account):
        """Test successful fund transfer"""
        initial_from_balance = account.balance
        initial_to_balance = savings_account.balance
        
        transaction = TransactionService.transfer_funds(
            from_account=account,
            to_account=savings_account,
            amount=Decimal('200.00'),
            description='Transfer to savings'
        )
        
        assert transaction.transaction_type == 'transfer'
        assert transaction.status == 'completed'
        assert transaction.account == account
        assert transaction.to_account == savings_account
        
        # Verify balances were updated
        account.refresh_from_db()
        savings_account.refresh_from_db()
        
        assert account.balance == initial_from_balance - Decimal('200.00')
        assert savings_account.balance == initial_to_balance + Decimal('200.00')
    
    def test_transfer_funds_insufficient_balance(self, account, savings_account):
        """Test transfer with insufficient funds"""
        account.balance = Decimal('50.00')
        account.save()
        
        with pytest.raises(ValueError, match='Insufficient funds'):
            TransactionService.transfer_funds(
                from_account=account,
                to_account=savings_account,
                amount=Decimal('100.00'),
                description='Transfer attempt'
            )


@pytest.mark.unit
class TestAnalyticsService:
    """Test analytics service"""
    
    def test_get_spending_by_category(self, account):
        """Test spending breakdown by category"""
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Create categories
        food_category = Category.objects.create(name='Food', color='#28a745')
        shopping_category = Category.objects.create(name='Shopping', color='#007bff')
        
        # Create transactions
        Transaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Groceries',
            transaction_type='debit',
            category=food_category,
            status='completed'
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('30.00'),
            description='Restaurant',
            transaction_type='debit',
            category=food_category,
            status='completed'
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Clothes',
            transaction_type='debit',
            category=shopping_category,
            status='completed'
        )
        
        # Transaction without category
        Transaction.objects.create(
            account=account,
            amount=Decimal('25.00'),
            description='Other',
            transaction_type='debit',
            status='completed'
        )
        
        # Credit transaction (should not be included)
        Transaction.objects.create(
            account=account,
            amount=Decimal('200.00'),
            description='Salary',
            transaction_type='credit',
            status='completed'
        )
        
        # Test spending breakdown
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now()
        
        spending = AnalyticsService.get_spending_by_category(
            account, start_date, end_date
        )
        
        assert spending['Food'] == Decimal('80.00')  # 50 + 30
        assert spending['Shopping'] == Decimal('100.00')
        assert spending['Uncategorized'] == Decimal('25.00')
        assert len(spending) == 3
    
    def test_get_monthly_trends(self, account):
        """Test monthly trends calculation"""
        from django.utils import timezone
        from datetime import datetime
        
        # Create transactions for different months
        # Current month
        Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Current spending',
            transaction_type='debit',
            status='completed',
            transaction_date=timezone.now()
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('500.00'),
            description='Current income',
            transaction_type='credit',
            status='completed',
            transaction_date=timezone.now()
        )
        
        # Previous month
        last_month = timezone.now() - timezone.timedelta(days=35)
        Transaction.objects.create(
            account=account,
            amount=Decimal('150.00'),
            description='Last month spending',
            transaction_type='debit',
            status='completed',
            transaction_date=last_month
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('600.00'),
            description='Last month income',
            transaction_type='credit',
            status='completed',
            transaction_date=last_month
        )
        
        trends = AnalyticsService.get_monthly_trends(account, months=2)
        
        # Should have data for both months
        assert len(trends) == 2
        
        # Check current month
        current_month_key = timezone.now().strftime('%Y-%m')
        assert trends[current_month_key]['spending'] == Decimal('100.00')
        assert trends[current_month_key]['income'] == Decimal('500.00')
        
        # Check previous month
        last_month_key = last_month.strftime('%Y-%m')
        assert trends[last_month_key]['spending'] == Decimal('150.00')
        assert trends[last_month_key]['income'] == Decimal('600.00')
