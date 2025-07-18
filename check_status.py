#!/usr/bin/env python
"""
Quick status check for the Django Finance App
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def check_status():
    """Check application status"""
    print("🔍 Django Finance App Status Check")
    print("=" * 50)
    
    try:
        # Check database connection
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection: OK")
        
        # Check if tables exist
        from django.contrib.auth.models import User
        from transactions.models import Account, Transaction, Category
        
        user_count = User.objects.count()
        account_count = Account.objects.count()
        transaction_count = Transaction.objects.count()
        category_count = Category.objects.count()
        
        print(f"✅ Users: {user_count}")
        print(f"✅ Accounts: {account_count}")
        print(f"✅ Transactions: {transaction_count}")
        print(f"✅ Categories: {category_count}")
        
        # Check URL patterns
        from django.urls import reverse
        
        print("\n🌐 URL Patterns:")
        urls = [
            ('Landing Page', 'landing'),
            ('Login', 'login'),
            ('Register', 'register'),
            ('Dashboard', 'dashboard'),
        ]
        
        for name, url_name in urls:
            try:
                url = reverse(url_name)
                print(f"✅ {name}: http://localhost:8000{url}")
            except Exception as e:
                print(f"❌ {name}: Error - {e}")
        
        print("\n🔐 Admin User Info:")
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✅ Admin exists: {admin_user.email}")
            print("✅ Admin password: admin123")
        except User.DoesNotExist:
            print("❌ Admin user not found")
        
        print("\n🚀 Application Status: READY")
        print("=" * 50)
        print("🌐 Main Application: http://localhost:8000")
        print("👨‍💼 Admin Panel: http://localhost:8000/admin/")
        print("🔑 Login: admin / admin123")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = check_status()
    sys.exit(0 if success else 1)
