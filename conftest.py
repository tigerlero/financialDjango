"""
Pytest configuration and fixtures
"""
import pytest
import os
import django
from django.conf import settings
from django.test import Client
from decimal import Decimal

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

from django.contrib.auth.models import User
from transactions.models import Account, Transaction, Category


@pytest.fixture
def user():
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Authenticated client"""
    client.login(username='testuser', password='testpass123')
    return client


@pytest.fixture
def category():
    """Create a test category"""
    return Category.objects.create(
        name='Food & Dining',
        color='#28a745'
    )


@pytest.fixture
def account(user):
    """Create a test account"""
    return Account.objects.create(
        user=user,
        name='Test Checking',
        account_type='checking',
        account_number='CHK123456',
        balance=Decimal('1000.00'),
        currency='USD'
    )


@pytest.fixture
def savings_account(user):
    """Create a test savings account"""
    return Account.objects.create(
        user=user,
        name='Test Savings',
        account_type='savings',
        account_number='SAV123456',
        balance=Decimal('5000.00'),
        currency='USD'
    )


@pytest.fixture
def transaction(account, category):
    """Create a test transaction"""
    return Transaction.objects.create(
        account=account,
        amount=Decimal('50.00'),
        description='Test transaction',
        transaction_type='debit',
        category=category,
        status='completed'
    )


@pytest.fixture
def mock_stripe_payment_intent():
    """Mock Stripe payment intent"""
    class MockPaymentIntent:
        def __init__(self):
            self.id = 'pi_test_123'
            self.client_secret = 'pi_test_123_secret'
            self.status = 'succeeded'
            self.payment_method = 'pm_test_123'
    
    return MockPaymentIntent()


@pytest.fixture
def api_client():
    """DRF API test client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Authenticated API client"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests"""
    pass
