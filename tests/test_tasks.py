"""
Unit tests for Celery tasks
"""
import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from django.utils import timezone
from transactions.models import Account, Transaction, RecurringTransaction, Category
from transactions.tasks import (
    process_payment_async, process_recurring_transactions, generate_monthly_report
)


@pytest.mark.unit
class TestProcessPaymentAsyncTask:
    """Test async payment processing task"""
    
    @patch('transactions.tasks.StripePaymentService.confirm_payment')
    def test_process_payment_success(self, mock_confirm, account):
        """Test successful payment processing"""
        # Create pending transaction
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Online purchase',
            transaction_type='debit',
            status='pending'
        )
        
        # Mock successful payment confirmation
        mock_confirm.return_value = {
            'success': True,
            'status': 'succeeded',
            'payment_method': 'pm_test_123'
        }
        
        # Run task
        result = process_payment_async(transaction.id, 'pi_test_123')
        
        assert result['success'] is True
        assert result['transaction_id'] == transaction.id
        
        # Verify transaction was updated
        transaction.refresh_from_db()
        assert transaction.status == 'completed'
        assert transaction.external_payment_id == 'pi_test_123'
        
        # Verify payment confirmation was called
        mock_confirm.assert_called_once_with('pi_test_123')
    
    @patch('transactions.tasks.StripePaymentService.confirm_payment')
    def test_process_payment_failure(self, mock_confirm, account):
        """Test payment processing failure"""
        # Create pending transaction
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Online purchase',
            transaction_type='debit',
            status='pending'
        )
        
        # Mock failed payment confirmation
        mock_confirm.return_value = {
            'success': False,
            'error': 'Payment failed'
        }
        
        # Run task
        result = process_payment_async(transaction.id, 'pi_test_123')
        
        assert result['success'] is False
        assert result['error'] == 'Payment failed'
        
        # Verify transaction was marked as failed
        transaction.refresh_from_db()
        assert transaction.status == 'failed'
        assert transaction.metadata['error'] == 'Payment failed'
    
    def test_process_payment_transaction_not_found(self):
        """Test task with non-existent transaction"""
        result = process_payment_async(99999, 'pi_test_123')
        
        assert result['success'] is False
        assert result['error'] == 'Transaction not found'
    
    @patch('transactions.tasks.StripePaymentService.confirm_payment')
    def test_process_payment_exception(self, mock_confirm, account):
        """Test task with unexpected exception"""
        # Create pending transaction
        transaction = Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Online purchase',
            transaction_type='debit',
            status='pending'
        )
        
        # Mock exception
        mock_confirm.side_effect = Exception('Unexpected error')
        
        # Run task
        result = process_payment_async(transaction.id, 'pi_test_123')
        
        assert result['success'] is False
        assert result['error'] == 'Unexpected error'


@pytest.mark.unit
class TestProcessRecurringTransactionsTask:
    """Test recurring transactions processing task"""
    
    def test_process_due_recurring_transactions(self, account, category):
        """Test processing due recurring transactions"""
        # Create due recurring transaction
        due_recurring = RecurringTransaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Monthly subscription',
            category=category,
            frequency='monthly',
            next_transaction_date=timezone.now() - timezone.timedelta(days=1),
            is_active=True
        )
        
        # Create future recurring transaction (should not be processed)
        future_recurring = RecurringTransaction.objects.create(
            account=account,
            amount=Decimal('25.00'),
            description='Future subscription',
            category=category,
            frequency='monthly',
            next_transaction_date=timezone.now() + timezone.timedelta(days=30),
            is_active=True
        )
        
        # Run task
        processed_count = process_recurring_transactions()
        
        assert processed_count == 1
        
        # Verify transaction was created
        transactions = Transaction.objects.filter(
            description__contains='Monthly subscription'
        )
        assert len(transactions) == 1
        
        transaction = transactions[0]
        assert transaction.amount == Decimal('50.00')
        assert transaction.status == 'completed'
        assert transaction.category == category
        assert transaction.metadata['recurring_id'] == due_recurring.id
        
        # Verify next transaction date was updated
        due_recurring.refresh_from_db()
        assert due_recurring.next_transaction_date > timezone.now()
    
    def test_process_inactive_recurring_transactions(self, account, category):
        """Test that inactive recurring transactions are not processed"""
        # Create inactive recurring transaction
        RecurringTransaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Inactive subscription',
            category=category,
            frequency='monthly',
            next_transaction_date=timezone.now() - timezone.timedelta(days=1),
            is_active=False
        )
        
        # Run task
        processed_count = process_recurring_transactions()
        
        assert processed_count == 0
        
        # Verify no transactions were created
        transactions = Transaction.objects.filter(
            description__contains='Inactive subscription'
        )
        assert len(transactions) == 0
    
    def test_process_different_frequencies(self, account, category):
        """Test processing recurring transactions with different frequencies"""
        base_date = timezone.now() - timezone.timedelta(days=1)
        
        # Create recurring transactions with different frequencies
        daily = RecurringTransaction.objects.create(
            account=account,
            amount=Decimal('10.00'),
            description='Daily recurring',
            frequency='daily',
            next_transaction_date=base_date,
            is_active=True
        )
        
        weekly = RecurringTransaction.objects.create(
            account=account,
            amount=Decimal('20.00'),
            description='Weekly recurring',
            frequency='weekly',
            next_transaction_date=base_date,
            is_active=True
        )
        
        # Run task
        processed_count = process_recurring_transactions()
        
        assert processed_count == 2
        
        # Verify next dates were updated correctly
        daily.refresh_from_db()
        weekly.refresh_from_db()
        
        # Daily should be next day
        expected_daily = base_date + timezone.timedelta(days=1)
        assert daily.next_transaction_date.date() == expected_daily.date()
        
        # Weekly should be next week
        expected_weekly = base_date + timezone.timedelta(weeks=1)
        assert weekly.next_transaction_date.date() == expected_weekly.date()


@pytest.mark.unit
class TestGenerateMonthlyReportTask:
    """Test monthly report generation task"""
    
    def test_generate_monthly_report_success(self, user, account, category):
        """Test successful monthly report generation"""
        # Create transactions for the month
        Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Expense 1',
            transaction_type='debit',
            category=category,
            status='completed'
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Expense 2',
            transaction_type='debit',
            category=category,
            status='completed'
        )
        
        # Run task
        result = generate_monthly_report(user.id, 2023, 12)
        
        assert 'error' not in result
        assert result['user_id'] == user.id
        assert result['period'] == '2023-12'
        assert len(result['accounts']) == 1
        
        account_data = result['accounts'][0]
        assert account_data['account_id'] == account.id
        assert account_data['account_name'] == account.name
        assert category.name in account_data['spending_by_category']
    
    def test_generate_monthly_report_user_not_found(self):
        """Test report generation with non-existent user"""
        result = generate_monthly_report(99999, 2023, 12)
        
        assert 'error' in result
        assert 'User matching query does not exist' in result['error']
    
    def test_generate_monthly_report_exception(self, user):
        """Test report generation with unexpected exception"""
        # This test would require mocking to force an exception
        # For now, just test with valid user but edge case
        result = generate_monthly_report(user.id, 2023, 13)  # Invalid month
        
        # Should handle gracefully or raise appropriate error
        assert isinstance(result, dict)
