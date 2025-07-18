#!/usr/bin/env python
"""
Create sample data for the Django Finance App
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def create_sample_data():
    """Create sample data for testing"""
    from django.contrib.auth.models import User
    from transactions.models import Account, Transaction, Category
    from decimal import Decimal
    
    print("🔄 Creating sample data...")
    
    try:
        # Get or create admin user
        admin_user = User.objects.get(username='admin')
        
        # Create categories
        categories = [
            ('Food & Dining', '#28a745'),
            ('Transportation', '#007bff'),
            ('Entertainment', '#ffc107'),
            ('Shopping', '#dc3545'),
            ('Bills & Utilities', '#6f42c1'),
            ('Healthcare', '#fd7e14'),
        ]
        
        created_categories = []
        for name, color in categories:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={'color': color}
            )
            created_categories.append(cat)
            if created:
                print(f"✅ Created category: {name}")
            else:
                print(f"✅ Category exists: {name}")
        
        # Create accounts
        accounts_data = [
            ('Checking Account', 'checking', 'CHK001', Decimal('1000.00')),
            ('Savings Account', 'savings', 'SAV001', Decimal('5000.00')),
            ('Credit Card', 'credit', 'CC001', Decimal('0.00')),
        ]
        
        created_accounts = []
        for name, acc_type, acc_number, balance in accounts_data:
            acc, created = Account.objects.get_or_create(
                user=admin_user,
                account_number=acc_number,
                defaults={
                    'name': name,
                    'account_type': acc_type,
                    'balance': balance
                }
            )
            created_accounts.append(acc)
            if created:
                print(f"✅ Created account: {name}")
            else:
                print(f"✅ Account exists: {name}")
        
        # Create sample transactions
        checking_account = created_accounts[0]  # Checking account
        food_category = created_categories[0]   # Food & Dining
        transport_category = created_categories[1]  # Transportation
        
        transactions_data = [
            (Decimal('2500.00'), 'Salary deposit', 'credit', None),
            (Decimal('50.00'), 'Grocery shopping', 'debit', food_category),
            (Decimal('25.00'), 'Coffee shop', 'debit', food_category),
            (Decimal('75.00'), 'Gas station', 'debit', transport_category),
            (Decimal('120.00'), 'Restaurant dinner', 'debit', food_category),
            (Decimal('40.00'), 'Uber ride', 'debit', transport_category),
        ]
        
        for amount, description, txn_type, category in transactions_data:
            txn, created = Transaction.objects.get_or_create(
                account=checking_account,
                description=description,
                defaults={
                    'amount': amount,
                    'transaction_type': txn_type,
                    'category': category,
                    'status': 'completed'
                }
            )
            if created:
                print(f"✅ Created transaction: {description}")
            else:
                print(f"✅ Transaction exists: {description}")
        
        print("\n🎉 Sample data created successfully!")
        
        # Print summary
        print("\n📊 Data Summary:")
        print(f"Users: {User.objects.count()}")
        print(f"Accounts: {Account.objects.count()}")
        print(f"Categories: {Category.objects.count()}")
        print(f"Transactions: {Transaction.objects.count()}")
        
        # Update account balances based on transactions
        for account in Account.objects.all():
            calculated_balance = account.get_balance()
            if account.balance != calculated_balance:
                account.balance = calculated_balance
                account.save()
                print(f"✅ Updated {account.name} balance: ${calculated_balance}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

if __name__ == "__main__":
    success = create_sample_data()
    sys.exit(0 if success else 1)
