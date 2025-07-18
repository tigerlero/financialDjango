#!/usr/bin/env python
"""
Fix admin user permissions
"""
import os
import sys
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
django.setup()

def fix_admin_user():
    """Fix admin user permissions"""
    from django.contrib.auth.models import User
    
    print("🔧 Fixing admin user permissions...")
    
    try:
        # Try to get existing admin user
        admin_user = User.objects.get(username='admin')
        print(f"✅ Found existing admin user: {admin_user.username}")
        
        # Update permissions
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        admin_user.set_password('admin123')
        admin_user.save()
        
        print("✅ Updated admin user permissions")
        
    except User.DoesNotExist:
        print("❌ Admin user not found, creating new one...")
        
        # Create new admin user
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        print("✅ Created new admin superuser")
    
    # Verify permissions
    admin_user.refresh_from_db()
    print(f"\n📊 Admin User Status:")
    print(f"Username: {admin_user.username}")
    print(f"Email: {admin_user.email}")
    print(f"Is superuser: {admin_user.is_superuser}")
    print(f"Is staff: {admin_user.is_staff}")
    print(f"Is active: {admin_user.is_active}")
    
    # Test admin URL
    from django.urls import reverse
    try:
        admin_url = reverse('admin:index')
        print(f"\n🌐 Admin URL: http://localhost:8000{admin_url}")
        print("🔑 Login: admin / admin123")
        print("\n✅ Admin setup complete!")
        return True
    except Exception as e:
        print(f"❌ Error with admin URL: {e}")
        return False

if __name__ == "__main__":
    success = fix_admin_user()
    sys.exit(0 if success else 1)
