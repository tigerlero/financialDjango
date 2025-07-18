# Django Finance App - Setup Guide

A comprehensive guide to set up and run the Django Finance Application with PostgreSQL, Redis, and Celery.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for cloning the repository)
- **Web Browser** (Chrome, Firefox, Safari, Edge)

### System Requirements

- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 2GB free space
- **OS**: Windows 10/11, macOS 10.14+, or Linux

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd djangoProject

# Make sure you're in the project directory
ls -la  # Should show docker-compose.yml, requirements.txt, etc.
```

### 2. Environment Configuration

Create a `.env` file (or use the provided one):

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your settings
# Note: For development, the default values should work
```

**Default Environment Variables:**
```env
DEBUG=True
SECRET_KEY=django-insecure-your-secret-key-here
DATABASE_URL=postgres://django:django123@db:5432/financeapp
REDIS_URL=redis://redis:6379/1
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### 4. Database Setup

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser account
docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com

# Set superuser password
docker-compose exec web python manage.py shell -c "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin123'); u.save()"
```

### 5. Create Sample Data (Optional)

```bash
# Create sample accounts, categories, and transactions
docker-compose exec web python manage.py shell -c "
from transactions.models import *
from django.contrib.auth.models import User
from decimal import Decimal

u = User.objects.get(username='admin')

# Create accounts
acc1 = Account.objects.create(user=u, name='Checking Account', account_type='checking', account_number='CHK001', balance=Decimal('1000.00'))
acc2 = Account.objects.create(user=u, name='Savings Account', account_type='savings', account_number='SAV001', balance=Decimal('5000.00'))

# Create categories
cat1 = Category.objects.create(name='Food & Dining', color='#28a745')
cat2 = Category.objects.create(name='Transportation', color='#007bff')
cat3 = Category.objects.create(name='Entertainment', color='#ffc107')

# Create sample transactions
Transaction.objects.create(account=acc1, amount=Decimal('50.00'), description='Grocery shopping', transaction_type='debit', category=cat1, status='completed')
Transaction.objects.create(account=acc1, amount=Decimal('2500.00'), description='Salary deposit', transaction_type='credit', status='completed')
Transaction.objects.create(account=acc1, amount=Decimal('25.00'), description='Coffee shop', transaction_type='debit', category=cat1, status='completed')

print('Sample data created successfully!')
"
```

### 6. Access the Application

🌐 **Main Application**: http://localhost:8000  
👨‍💼 **Admin Panel**: http://localhost:8000/admin/  
🔑 **Login**: `admin` / `admin123`

---

## 💻 Local Development Setup (Without Docker)

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Node.js (for frontend tools, optional)

### 1. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install additional development dependencies
pip install pytest-cov black flake8 mypy
```

### 3. Database Setup

```bash
# Start PostgreSQL service
# On Windows: net start postgresql
# On macOS: brew services start postgresql
# On Linux: sudo systemctl start postgresql

# Create database
psql -U postgres -c "CREATE DATABASE financeapp;"
psql -U postgres -c "CREATE USER django WITH PASSWORD 'django123';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE financeapp TO django;"
```

### 4. Redis Setup

```bash
# Start Redis service
# On Windows: Download and install Redis for Windows
# On macOS: brew services start redis
# On Linux: sudo systemctl start redis
```

### 5. Environment Configuration

```bash
# Create .env file for local development
cat > .env << EOF
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://django:django123@localhost:5432/financeapp
REDIS_URL=redis://localhost:6379/1
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
```

### 6. Run Application

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# In another terminal, start Celery worker
celery -A financeapp worker --loglevel=info

# In another terminal, start Celery beat (optional)
celery -A financeapp beat --loglevel=info
```

---

## 🧪 Testing

### Run All Tests

```bash
# Using Docker
docker-compose exec web python -m pytest tests/ -v

# Local development
python -m pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
python -m pytest tests/ -m unit -v

# Integration tests only
python -m pytest tests/ -m integration -v

# API tests only
python -m pytest tests/ -m api -v
```

### Test Coverage

```bash
# Run tests with coverage report
docker-compose exec web python -m pytest tests/ --cov=transactions --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser
```

---

## 🔧 Configuration

### Stripe Configuration

1. **Create Stripe Account**: Go to https://stripe.com and create an account
2. **Get API Keys**: Navigate to Developers → API Keys
3. **Update Environment Variables**:
   ```env
   STRIPE_SECRET_KEY=sk_test_your_actual_secret_key
   STRIPE_PUBLIC_KEY=pk_test_your_actual_public_key
   ```

### Email Configuration (Optional)

Add to your `.env` file:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Production Settings

For production deployment, update these settings:

```env
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@production-db:5432/financeapp
REDIS_URL=redis://production-redis:6379/1
```

---

## 🐳 Docker Commands Reference

### Container Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ This will delete your data)
docker-compose down -v

# Rebuild containers
docker-compose build

# View logs
docker-compose logs -f web      # Web server logs
docker-compose logs -f celery   # Celery worker logs
docker-compose logs -f db       # Database logs
```

### Database Operations

```bash
# Access database shell
docker-compose exec db psql -U django -d financeapp

# Create database backup
docker-compose exec db pg_dump -U django financeapp > backup.sql

# Restore database backup
docker-compose exec -T db psql -U django financeapp < backup.sql

# Run Django migrations
docker-compose exec web python manage.py migrate

# Create new migration
docker-compose exec web python manage.py makemigrations
```

### Django Management

```bash
# Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run custom management command
docker-compose exec web python manage.py your_custom_command
```

---

## 📊 Monitoring and Logs

### Application Logs

```bash
# View real-time logs
docker-compose logs -f web

# View last 100 lines
docker-compose logs --tail=100 web

# View logs for specific service
docker-compose logs celery
```

### Performance Monitoring

```bash
# Check container resource usage
docker stats

# View running containers
docker-compose ps

# Execute commands in running container
docker-compose exec web bash
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
Error: bind: address already in use
```
**Solution**: Stop the service using the port or change ports in `docker-compose.yml`

#### 2. Database Connection Error
```bash
Error: could not connect to server: Connection refused
```
**Solutions**:
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check database credentials in `.env`
- Restart containers: `docker-compose down && docker-compose up`

#### 3. Redis Connection Error
```bash
Error: Error connecting to Redis
```
**Solutions**:
- Ensure Redis container is running
- Check Redis URL in `.env`
- Restart Redis: `docker-compose restart redis`

#### 4. Permission Denied (Windows)
```bash
Error: permission denied
```
**Solutions**:
- Run Docker Desktop as Administrator
- Ensure Docker has access to the project directory
- Check Windows file sharing settings

#### 5. Celery Worker Not Starting
```bash
Error: ImportError in Celery worker
```
**Solutions**:
- Check for circular imports in code
- Ensure all dependencies are installed
- Restart Celery: `docker-compose restart celery`

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Add to .env file
DEBUG=True

# View detailed logs
docker-compose logs -f web
```

### Reset Everything

If you need to completely reset the application:

```bash
# Stop all containers and remove volumes
docker-compose down -v

# Remove all images
docker-compose rm -f

# Rebuild and start fresh
docker-compose up --build
```

---

## 🔒 Security Considerations

### Development vs Production

**Development** (Current setup):
- Debug mode enabled
- Default secret key
- Permissive CORS settings
- Test Stripe keys

**Production Checklist**:
- [ ] Set `DEBUG=False`
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use production database
- [ ] Set up SSL/TLS
- [ ] Configure proper logging
- [ ] Use production Stripe keys
- [ ] Set up monitoring

### Environment Variables Security

Never commit sensitive information to version control:
- Add `.env` to `.gitignore`
- Use environment-specific configuration
- Rotate secrets regularly

---

## 🎯 Next Steps

After successful setup, you can:

1. **Explore the Admin Panel**: http://localhost:8000/admin/
2. **Create User Accounts**: Add new users and accounts
3. **Test Transactions**: Create, update, and transfer funds
4. **View Analytics**: Check spending reports and trends
5. **Integrate APIs**: Add your Stripe keys for payment processing
6. **Customize**: Modify templates, add features, or extend functionality

## 📚 Additional Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Stripe API**: https://stripe.com/docs/api
- **Celery Documentation**: https://docs.celeryproject.org/
- **Docker Documentation**: https://docs.docker.com/

---

## 💡 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the logs: `docker-compose logs -f web`
3. Ensure all prerequisites are met
4. Verify your `.env` configuration
5. Try resetting the environment completely

Happy coding! 🚀
