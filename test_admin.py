#!/usr/bin/env python
"""
Test admin functionality
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def test_admin():
    """Test admin functionality"""
    print("🔍 Testing Admin Functionality")
    print("=" * 50)
    
    try:
        # Test admin user
        from django.contrib.auth.models import User
        admin_user = User.objects.get(username='admin')
        
        print(f"✅ Admin User: {admin_user.username}")
        print(f"   - Email: {admin_user.email}")
        print(f"   - Is superuser: {admin_user.is_superuser}")
        print(f"   - Is staff: {admin_user.is_staff}")
        print(f"   - Is active: {admin_user.is_active}")
        
        # Test admin URLs
        from django.urls import reverse
        
        admin_urls = [
            ('Admin Index', 'admin:index'),
            ('Admin Login', 'admin:login'),
            ('User Admin', 'admin:auth_user_changelist'),
            ('Account Admin', 'admin:transactions_account_changelist'),
            ('Transaction Admin', 'admin:transactions_transaction_changelist'),
            ('Category Admin', 'admin:transactions_category_changelist'),
        ]
        
        print(f"\n🌐 Admin URLs:")
        for name, url_name in admin_urls:
            try:
                url = reverse(url_name)
                print(f"   ✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"   ❌ {name}: Error - {e}")
        
        # Test admin models
        from transactions.models import Account, Transaction, Category
        
        print(f"\n📊 Data Summary:")
        print(f"   - Users: {User.objects.count()}")
        print(f"   - Accounts: {Account.objects.count()}")
        print(f"   - Transactions: {Transaction.objects.count()}")
        print(f"   - Categories: {Category.objects.count()}")
        
        # Test admin site configuration
        from django.contrib import admin
        print(f"\n⚙️ Admin Site Configuration:")
        print(f"   - Site header: {admin.site.site_header}")
        print(f"   - Site title: {admin.site.site_title}")
        print(f"   - Index title: {admin.site.index_title}")
        
        # Test model admin registrations
        print(f"\n📝 Registered Models:")
        for model, admin_class in admin.site._registry.items():
            print(f"   ✅ {model._meta.label}: {admin_class.__class__.__name__}")
        
        print(f"\n🎉 Admin functionality test complete!")
        print("=" * 50)
        print("🌐 Admin Panel: http://localhost:8000/admin/")
        print("🔑 Login: admin / admin123")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_admin()
    sys.exit(0 if success else 1)
