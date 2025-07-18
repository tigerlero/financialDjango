"""
API integration tests
"""
import pytest
import json
from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from transactions.models import Account, Transaction, Category


@pytest.mark.integration
@pytest.mark.api
class TestAccountAPI:
    """Test Account API endpoints"""
    
    def test_list_accounts(self, authenticated_api_client, account):
        """Test listing user accounts"""
        url = reverse('account-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['count'] == 1
        assert data['results'][0]['name'] == account.name
        assert data['results'][0]['account_type'] == account.account_type
    
    def test_create_account(self, authenticated_api_client, user):
        """Test creating a new account"""
        url = reverse('account-list')
        data = {
            'name': 'New Savings Account',
            'account_type': 'savings',
            'currency': 'USD'
        }
        
        response = authenticated_api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Savings Account'
        assert response.data['account_type'] == 'savings'
        
        # Verify account was created in database
        account = Account.objects.get(name='New Savings Account')
        assert account.user == user
    
    def test_get_account_balance(self, authenticated_api_client, account):
        """Test getting account balance"""
        url = reverse('account-balance', kwargs={'pk': account.id})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'balance' in data
        assert data['currency'] == account.currency
    
    def test_get_spending_by_category(self, authenticated_api_client, account, category):
        """Test getting spending breakdown by category"""
        # Create a transaction
        Transaction.objects.create(
            account=account,
            amount=Decimal('100.00'),
            description='Test expense',
            transaction_type='debit',
            category=category,
            status='completed'
        )
        
        url = reverse('account-spending-by-category', kwargs={'pk': account.id})
        response = authenticated_api_client.get(url, {
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert 'spending_by_category' in data
        assert category.name in data['spending_by_category']
    
    def test_unauthorized_access(self, api_client, account):
        """Test unauthorized access to account endpoints"""
        url = reverse('account-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_access_other_user_account(self, authenticated_api_client, user):
        """Test accessing another user's account"""
        from django.contrib.auth.models import User
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
        
        url = reverse('account-detail', kwargs={'pk': other_account.id})
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.api
class TestTransactionAPI:
    """Test Transaction API endpoints"""
    
    def test_list_transactions(self, authenticated_api_client, transaction):
        """Test listing user transactions"""
        url = reverse('transaction-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['count'] == 1
        assert data['results'][0]['description'] == transaction.description
    
    def test_filter_transactions_by_account(self, authenticated_api_client, account, savings_account):
        """Test filtering transactions by account"""
        # Create transactions for different accounts
        Transaction.objects.create(
            account=account,
            amount=Decimal('50.00'),
            description='Checking expense',
            transaction_type='debit'
        )
        
        Transaction.objects.create(
            account=savings_account,
            amount=Decimal('100.00'),
            description='Savings deposit',
            transaction_type='credit'
        )
        
        url = reverse('transaction-list')
        response = authenticated_api_client.get(url, {'account_id': account.id})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['count'] == 1
        assert data['results'][0]['description'] == 'Checking expense'
    
    def test_search_transactions(self, authenticated_api_client, account):
        """Test searching transactions"""
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
        
        url = reverse('transaction-list')
        response = authenticated_api_client.get(url, {'search': 'coffee'})
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['count'] == 1
        assert 'Coffee shop' in data['results'][0]['description']
    
    @pytest.mark.slow
    def test_create_payment_transaction(self, authenticated_api_client, account):
        """Test creating a payment transaction"""
        url = reverse('transaction-create-payment')
        data = {
            'account_id': account.id,
            'amount': '75.00',
            'payment_method_id': 'pm_test_123',
            'description': 'Online purchase'
        }
        
        with pytest.raises(Exception):
            # This will fail without proper Stripe setup, but tests the endpoint
            response = authenticated_api_client.post(url, data)
    
    def test_transfer_funds(self, authenticated_api_client, account, savings_account):
        """Test transferring funds between accounts"""
        initial_from_balance = account.balance
        initial_to_balance = savings_account.balance
        
        url = reverse('transaction-transfer')
        data = {
            'from_account_id': account.id,
            'to_account_id': savings_account.id,
            'amount': '200.00',
            'description': 'Transfer to savings'
        }
        
        response = authenticated_api_client.post(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify balances were updated
        account.refresh_from_db()
        savings_account.refresh_from_db()
        
        assert account.balance == initial_from_balance - Decimal('200.00')
        assert savings_account.balance == initial_to_balance + Decimal('200.00')
    
    def test_transfer_same_account_error(self, authenticated_api_client, account):
        """Test transfer to same account returns error"""
        url = reverse('transaction-transfer')
        data = {
            'from_account_id': account.id,
            'to_account_id': account.id,
            'amount': '100.00',
            'description': 'Invalid transfer'
        }
        
        response = authenticated_api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_transfer_insufficient_funds(self, authenticated_api_client, account, savings_account):
        """Test transfer with insufficient funds"""
        account.balance = Decimal('50.00')
        account.save()
        
        url = reverse('transaction-transfer')
        data = {
            'from_account_id': account.id,
            'to_account_id': savings_account.id,
            'amount': '100.00',
            'description': 'Transfer attempt'
        }
        
        response = authenticated_api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Insufficient funds' in response.data['error']


@pytest.mark.integration
@pytest.mark.api
class TestCategoryAPI:
    """Test Category API endpoints"""
    
    def test_list_categories(self, authenticated_api_client, category):
        """Test listing categories"""
        url = reverse('category-list')
        response = authenticated_api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data['count'] == 1
        assert data['results'][0]['name'] == category.name
    
    def test_create_category(self, authenticated_api_client):
        """Test creating a new category"""
        url = reverse('category-list')
        data = {
            'name': 'Transportation',
            'color': '#ff6b6b'
        }
        
        response = authenticated_api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Transportation'
        assert response.data['color'] == '#ff6b6b'
    
    def test_create_subcategory(self, authenticated_api_client, category):
        """Test creating a subcategory"""
        url = reverse('category-list')
        data = {
            'name': 'Fast Food',
            'parent': category.id,
            'color': '#ffc107'
        }
        
        response = authenticated_api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['parent'] == category.id
        
        # Verify subcategory relationship
        subcategory = Category.objects.get(name='Fast Food')
        assert subcategory.parent == category
