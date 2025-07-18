#!/usr/bin/env python
"""
Setup script for the Django Finance App
"""
import os
import sys
import subprocess

def run_command(cmd, description):
    """Run a command with description"""
    print(f"🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        print(f"Error: {result.stderr}")
        return False
    else:
        print(f"✅ Success: {description}")
        return True

def main():
    """Main setup function"""
    print("🚀 Setting up Django Finance App...")
    
    # Check if Docker is installed
    if not run_command("docker --version", "Checking Docker installation"):
        print("Please install Docker first")
        sys.exit(1)
    
    # Check if docker-compose is available
    if not run_command("docker-compose --version", "Checking Docker Compose installation"):
        print("Please install Docker Compose first")
        sys.exit(1)
    
    # Build and start containers
    if not run_command("docker-compose up -d --build", "Building and starting containers"):
        sys.exit(1)
    
    # Wait for database to be ready
    print("⏳ Waiting for database to be ready...")
    subprocess.run(["timeout", "30", "docker-compose", "exec", "db", "pg_isready", "-U", "django"], 
                   stderr=subprocess.DEVNULL)
    
    # Run migrations
    run_command("docker-compose exec web python manage.py migrate", "Running database migrations")
    
    # Create superuser
    run_command("docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com", 
                "Creating superuser")
    
    # Set superuser password
    run_command("docker-compose exec web python manage.py shell -c \"from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin123'); u.save()\"", 
                "Setting superuser password")
    
    # Create some sample data
    run_command("docker-compose exec web python manage.py shell -c \"from transactions.models import *; from django.contrib.auth.models import User; u = User.objects.get(username='admin'); Account.objects.create(user=u, name='Checking Account', account_type='checking', account_number='CHK001', balance=1000.00); Account.objects.create(user=u, name='Savings Account', account_type='savings', account_number='SAV001', balance=5000.00); Category.objects.create(name='Food & Dining', color='#28a745'); Category.objects.create(name='Transportation', color='#007bff'); Category.objects.create(name='Entertainment', color='#ffc107');\"", 
                "Creating sample data")
    
    print("\n🎉 Setup complete!")
    print("=" * 50)
    print("🌐 Application: http://localhost:8000")
    print("👨‍💼 Admin Panel: http://localhost:8000/admin/")
    print("🔑 Username: admin")
    print("🔑 Password: admin123")
    print("=" * 50)
    print("\n📋 Available commands:")
    print("• docker-compose logs -f web    # View web logs")
    print("• docker-compose logs -f celery # View celery logs")
    print("• docker-compose exec web python manage.py shell # Django shell")
    print("• docker-compose exec web python -m pytest tests/ # Run tests")
    print("• docker-compose down          # Stop all containers")
    print("• docker-compose down -v       # Stop and remove volumes")

if __name__ == "__main__":
    main()
