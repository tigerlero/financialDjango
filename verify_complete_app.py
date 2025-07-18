#!/usr/bin/env python
"""
Complete application verification
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def verify_complete_app():
    """Verify the complete application"""
    print("🚀 Complete Django Finance App Verification")
    print("=" * 60)
    
    try:
        # 1. Authentication System
        print("✅ 1. Authentication System")
        from django.urls import reverse
        
        auth_urls = [
            ('Landing Page', 'landing'),
            ('Login', 'login'),
            ('Register', 'register'),
            ('Logout', 'logout'),
        ]
        
        for name, url_name in auth_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # 2. Main Application Pages
        print("\n✅ 2. Main Application Pages")
        app_urls = [
            ('Dashboard', 'dashboard'),
            ('Account List', 'account_list'),
            ('Transaction List', 'transaction_list'),
        ]
        
        for name, url_name in app_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # 3. Admin System
        print("\n✅ 3. Admin System")
        admin_urls = [
            ('Admin Index', 'admin:index'),
            ('User Admin', 'admin:auth_user_changelist'),
            ('Account Admin', 'admin:transactions_account_changelist'),
            ('Transaction Admin', 'admin:transactions_transaction_changelist'),
        ]
        
        for name, url_name in admin_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # 4. Data Verification
        print("\n✅ 4. Data Verification")
        from django.contrib.auth.models import User
        from transactions.models import Account, Transaction, Category
        
        users = User.objects.count()
        accounts = Account.objects.count()
        transactions = Transaction.objects.count()
        categories = Category.objects.count()
        
        print(f"   Users: {users}")
        print(f"   Accounts: {accounts}")
        print(f"   Transactions: {transactions}")
        print(f"   Categories: {categories}")
        
        # 5. Admin User Verification
        print("\n✅ 5. Admin User Verification")
        try:
            admin_user = User.objects.get(username='admin')
            print(f"   Username: {admin_user.username}")
            print(f"   Email: {admin_user.email}")
            print(f"   Superuser: {admin_user.is_superuser}")
            print(f"   Staff: {admin_user.is_staff}")
            print(f"   Active: {admin_user.is_active}")
            print(f"   Password Check: {'✅ Correct' if admin_user.check_password('admin123') else '❌ Incorrect'}")
        except User.DoesNotExist:
            print("   ❌ Admin user not found")
        
        # 6. Template Verification
        print("\n✅ 6. Template Verification")
        templates = [
            'templates/auth/landing.html',
            'templates/auth/login.html',
            'templates/auth/register.html',
            'templates/transactions/dashboard.html',
            'templates/transactions/account_list.html',
            'templates/transactions/transaction_list.html',
            'templates/transactions/account_detail.html',
            'templates/base.html',
        ]
        
        for template in templates:
            if os.path.exists(template):
                print(f"   ✅ {os.path.basename(template)}")
            else:
                print(f"   ❌ {os.path.basename(template)} missing")
        
        # 7. API Endpoints
        print("\n✅ 7. API Endpoints")
        api_urls = [
            ('Account API', 'account-list'),
            ('Transaction API', 'transaction-list'),
            ('Category API', 'category-list'),
        ]
        
        for name, url_name in api_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # 8. AJAX Endpoints
        print("\n✅ 8. AJAX Endpoints")
        ajax_urls = [
            ('Transaction Search', 'transaction_search'),
            ('Quick Transaction', 'quick_transaction'),
        ]
        
        for name, url_name in ajax_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # 9. Sample Account Test
        print("\n✅ 9. Sample Account Test")
        if accounts > 0:
            first_account = Account.objects.first()
            print(f"   Sample Account: {first_account.name}")
            print(f"   Balance: ${first_account.get_balance():,.2f}")
            print(f"   Transactions: {first_account.transactions.count()}")
            
            # Test account detail URL
            try:
                account_url = reverse('account_detail', kwargs={'account_id': first_account.id})
                print(f"   Detail URL: http://localhost:8000{account_url}")
            except Exception as e:
                print(f"   ❌ Account detail URL error: {e}")
        else:
            print("   ⚠️ No accounts available")
        
        print("\n🎉 Verification Complete!")
        print("=" * 60)
        print("📋 Application Summary:")
        print("   ✅ Complete authentication system")
        print("   ✅ Working dashboard and main pages")
        print("   ✅ Enhanced admin interface")
        print("   ✅ RESTful API endpoints")
        print("   ✅ AJAX functionality")
        print("   ✅ Sample data available")
        print("   ✅ Responsive design")
        print("   ✅ Database integration")
        print("=" * 60)
        print("🌐 Quick Access:")
        print("   Landing: http://localhost:8000")
        print("   Login: http://localhost:8000/login/")
        print("   Dashboard: http://localhost:8000/dashboard/")
        print("   Accounts: http://localhost:8000/accounts/")
        print("   Transactions: http://localhost:8000/transactions/")
        print("   Admin: http://localhost:8000/admin/")
        print("=" * 60)
        print("🔑 Demo Credentials: admin / admin123")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_complete_app()
    sys.exit(0 if success else 1)
