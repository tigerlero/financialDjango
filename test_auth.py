#!/usr/bin/env python
"""
Test script to verify authentication setup
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def test_auth():
    """Test authentication setup"""
    try:
        # Test URL patterns
        from django.urls import reverse
        
        urls_to_test = [
            'landing',
            'login',
            'register',
            'logout',
            'dashboard'
        ]
        
        print("Testing URL patterns...")
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                print(f"✅ {url_name}: {url}")
            except Exception as e:
                print(f"❌ {url_name}: Error - {e}")
        
        # Test user creation
        from django.contrib.auth.models import User
        
        print("\nTesting user creation...")
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@test.com'}
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print("✅ Test user created successfully")
        else:
            print("✅ Test user already exists")
        
        print("\nAuthentication setup appears to be working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_auth()
    sys.exit(0 if success else 1)
