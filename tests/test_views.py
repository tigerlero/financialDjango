"""
Integration tests for Django views
"""
import pytest
import json
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth.models import User
from transactions.models import Account, Transaction, Category


@pytest.mark.integration
class TestDashboardView:
    """Test dashboard view"""
    
    def test_dashboard_authenticated(self, authenticated_client, account, transaction):
        """Test dashboard view with authenticated user"""
        url = reverse('dashboard')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert 'accounts' in response.context
        assert 'recent_transactions' in response.context
        assert 'total_balance' in response.context
        
        # Check template used
        assert 'transactions/dashboard.html' in [t.name for t in response.templates]
    
    def test_dashboard_unauthenticated(self, client):
        """Test dashboard view redirects unauthenticated users"""
        url = reverse('dashboard')
        response = client.get(url)
        
        assert response.status_code == 302
        assert '/admin/login/' in response.url
    
    def test_dashboard_context_data(self, authenticated_client, account, transaction):
        """Test dashboard context data"""
        url = reverse('dashboard')
        response = authenticated_client.get(url)
        
        accounts = response.context['accounts']
        transactions = response.context['recent_transactions']
        
        assert len(accounts) == 1
        assert accounts[0] == account
        assert len(transactions) == 1
        assert transactions[0] == transaction


@pytest.mark.integration
class TestAccountDetailView:
    """Test account detail view"""
    
    def test_account_detail_authenticated(self, authenticated_client, account):
        """Test account detail view with authenticated user"""
        url = reverse('account_detail', kwargs={'account_id': account.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        assert response.context['account'] == account
        assert 'transactions' in response.context
        assert 'current_balance' in response.context
    
    def test_account_detail_other_user(self, authenticated_client, user):
        """Test accessing another user's account detail"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )
        
        other_account = Account.objects.create(
            user=other_user,
            name='Other Account',
            account_type='checking',
            account_number='OTHER123'
        )
        
        url = reverse('account_detail', kwargs={'account_id': other_account.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == 404
    
    def test_account_detail_nonexistent(self, authenticated_client):
        """Test accessing non-existent account"""
        url = reverse('account_detail', kwargs={'account_id': 99999})
        response = authenticated_client.get(url)
        
        assert response.status_code == 404


@pytest.mark.integration
class TestTransactionSearchView:
    """Test transaction search AJAX endpoint"""
    
    def test_transaction_search_basic(self, authenticated_client, account):
        """Test basic transaction search"""
        # Create test transactions
        Transaction.objects.create(
            account=account,
            amount=Decimal('25.00'),
            description='Coffee shop',
            transaction_type='debit'
        )
        
        Transaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Grocery store',
            transaction_type='debit'
        )
        
        url = reverse('transaction_search')
        response = authenticated_client.get(url, {'q': 'coffee'})
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['transactions']) == 1
        assert 'Coffee shop' in data['transactions'][0]['description']
    
    def test_transaction_search_by_account(self, authenticated_client, account, savings_account):
        """Test transaction search filtered by account"""
        # Create transactions for different accounts
        Transaction.objects.create(
            account=account,
            amount=Decimal('30.00'),
            description='Checking transaction',
            transaction_type='debit'
        )
        
        Transaction.objects.create(
            account=savings_account,
            amount=Decimal('100.00'),
            description='Savings transaction',
            transaction_type='credit'
        )
        
        url = reverse('transaction_search')
        response = authenticated_client.get(url, {'account_id': account.id})
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['transactions']) == 1
        assert data['transactions'][0]['account'] == account.name
    
    def test_transaction_search_empty_query(self, authenticated_client, account, transaction):
        """Test transaction search with empty query"""
        url = reverse('transaction_search')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return all transactions (limited to 20)
        assert len(data['transactions']) == 1
    
    def test_transaction_search_no_results(self, authenticated_client, account):
        """Test transaction search with no results"""
        url = reverse('transaction_search')
        response = authenticated_client.get(url, {'q': 'nonexistent'})
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data['transactions']) == 0


@pytest.mark.integration
class TestQuickTransactionView:
    """Test quick transaction AJAX endpoint"""
    
    def test_quick_transaction_credit(self, authenticated_client, account):
        """Test creating a credit transaction"""
        initial_balance = account.balance
        
        url = reverse('quick_transaction')
        data = {
            'account_id': account.id,
            'amount': '100.00',
            'description': 'Salary bonus',
            'transaction_type': 'credit'
        }
        
        response = authenticated_client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data['success'] is True
        assert 'transaction_id' in response_data
        assert 'reference_number' in response_data
        
        # Verify transaction was created and completed
        transaction = Transaction.objects.get(id=response_data['transaction_id'])
        assert transaction.amount == Decimal('100.00')
        assert transaction.description == 'Salary bonus'
        assert transaction.transaction_type == 'credit'
        assert transaction.status == 'completed'
        
        # Verify balance was updated
        account.refresh_from_db()
        assert account.balance == initial_balance + Decimal('100.00')
    
    def test_quick_transaction_debit(self, authenticated_client, account):
        """Test creating a debit transaction"""
        url = reverse('quick_transaction')
        data = {
            'account_id': account.id,
            'amount': '50.00',
            'description': 'Groceries',
            'transaction_type': 'debit'
        }
        
        response = authenticated_client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data['success'] is True
        
        # Verify transaction was created (but not auto-completed for debit)
        transaction = Transaction.objects.get(id=response_data['transaction_id'])
        assert transaction.amount == Decimal('50.00')
        assert transaction.transaction_type == 'debit'
        assert transaction.status == 'pending'  # Debit transactions start as pending
    
    def test_quick_transaction_with_category(self, authenticated_client, account, category):
        """Test creating transaction with category"""
        url = reverse('quick_transaction')
        data = {
            'account_id': account.id,
            'amount': '75.00',
            'description': 'Restaurant meal',
            'transaction_type': 'debit',
            'category_id': category.id
        }
        
        response = authenticated_client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        assert response_data['success'] is True
        
        # Verify transaction has category
        transaction = Transaction.objects.get(id=response_data['transaction_id'])
        assert transaction.category == category
    
    def test_quick_transaction_invalid_account(self, authenticated_client, user):
        """Test creating transaction with invalid account"""
        url = reverse('quick_transaction')
        data = {
            'account_id': 99999,
            'amount': '100.00',
            'description': 'Invalid account',
            'transaction_type': 'credit'
        }
        
        response = authenticated_client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = response.json()
        
        assert response_data['success'] is False
        assert 'error' in response_data
    
    def test_quick_transaction_other_user_account(self, authenticated_client, user):
        """Test creating transaction with another user's account"""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password123'
        )
        
        other_account = Account.objects.create(
            user=other_user,
            name='Other Account',
            account_type='checking',
            account_number='OTHER123'
        )
        
        url = reverse('quick_transaction')
        data = {
            'account_id': other_account.id,
            'amount': '100.00',
            'description': 'Unauthorized transaction',
            'transaction_type': 'credit'
        }
        
        response = authenticated_client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = response.json()
        
        assert response_data['success'] is False
    
    def test_quick_transaction_invalid_json(self, authenticated_client):
        """Test quick transaction with invalid JSON"""
        url = reverse('quick_transaction')
        
        response = authenticated_client.post(
            url,
            'invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        response_data = response.json()
        
        assert response_data['success'] is False
        assert 'error' in response_data
    
    def test_quick_transaction_unauthenticated(self, client):
        """Test quick transaction without authentication"""
        url = reverse('quick_transaction')
        data = {
            'account_id': 1,
            'amount': '100.00',
            'description': 'Test',
            'transaction_type': 'credit'
        }
        
        response = client.post(
            url,
            json.dumps(data),
            content_type='application/json'
        )
        
        assert response.status_code == 302  # Redirect to login
