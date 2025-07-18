#!/usr/bin/env python
"""
Test account and transaction pages
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def test_pages():
    """Test account and transaction pages"""
    print("🔍 Testing Account and Transaction Pages")
    print("=" * 50)
    
    try:
        # Test URL patterns
        from django.urls import reverse
        
        urls_to_test = [
            ('Account List', 'account_list'),
            ('Transaction List', 'transaction_list'),
            ('Dashboard', 'dashboard'),
        ]
        
        print("✅ URL Pattern Test:")
        for name, url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # Test view functions exist
        from transactions import views
        
        print("\n✅ View Function Test:")
        view_functions = [
            'account_list',
            'transaction_list',
            'account_detail',
            'dashboard'
        ]
        
        for view_name in view_functions:
            if hasattr(views, view_name):
                print(f"   ✅ {view_name}: Function exists")
            else:
                print(f"   ❌ {view_name}: Function missing")
        
        # Test templates exist
        import os
        
        print("\n✅ Template Test:")
        templates_to_check = [
            'templates/transactions/account_list.html',
            'templates/transactions/transaction_list.html',
            'templates/transactions/account_detail.html',
            'templates/transactions/dashboard.html'
        ]
        
        for template in templates_to_check:
            if os.path.exists(template):
                print(f"   ✅ {template}: Template exists")
            else:
                print(f"   ❌ {template}: Template missing")
        
        # Test data for views
        from django.contrib.auth.models import User
        from transactions.models import Account, Transaction
        
        print("\n✅ Data Test:")
        user_count = User.objects.count()
        account_count = Account.objects.count()
        transaction_count = Transaction.objects.count()
        
        print(f"   Users: {user_count}")
        print(f"   Accounts: {account_count}")
        print(f"   Transactions: {transaction_count}")
        
        if account_count > 0:
            print("   ✅ Sample accounts available for testing")
        else:
            print("   ⚠️ No accounts available - create some for better testing")
        
        if transaction_count > 0:
            print("   ✅ Sample transactions available for testing")
        else:
            print("   ⚠️ No transactions available - create some for better testing")
        
        print("\n🎉 Page Test Complete!")
        print("=" * 50)
        print("📋 Available Pages:")
        print("🏠 Dashboard: http://localhost:8000/dashboard/")
        print("🏦 Accounts: http://localhost:8000/accounts/")
        print("💳 Transactions: http://localhost:8000/transactions/")
        print("👨‍💼 Admin: http://localhost:8000/admin/")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pages()
    sys.exit(0 if success else 1)
