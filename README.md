<img width="1436" height="423" alt="image" src="https://github.com/user-attachments/assets/ce1a1227-3342-40fb-a849-86e921bc92a9" /># Finance Management Application

A comprehensive Django-based personal finance management system with modern UI, real-time analytics, and robust financial tracking capabilities.

## 📸 Application Screenshots

### Dashboard Overview
<img width="1884" height="885" alt="image" src="https://github.com/user-attachments/assets/85ed6a08-b1f5-4b81-aea8-03daf772a9e0" />
<img width="1596" height="510" alt="image" src="https://github.com/user-attachments/assets/af97a637-1e7c-4978-ae5b-3dfd9bb43c10" />


*Main dashboard showing account balances, recent transactions, and quick actions*

### Transaction Management
<img width="1856" height="873" alt="image" src="https://github.com/user-attachments/assets/f1242298-43d6-4f62-af71-6e2f2210be33" />

*Transaction listing with filtering and search capabilities*

<img width="536" height="539" alt="image" src="https://github.com/user-attachments/assets/41e29121-a977-4eff-9aee-4d7e076524f0" />

*Transaction creation form with category selection and validation*

### Analytics & Reports
<img width="1601" height="767" alt="image" src="https://github.com/user-attachments/assets/324214fa-cdcf-4ec4-8868-1e960e6d6121" />
<img width="1570" height="402" alt="image" src="https://github.com/user-attachments/assets/8090b2d9-0203-4546-a0ff-f384c7eb63d5" />

### Account Management
<img width="1877" height="876" alt="image" src="https://github.com/user-attachments/assets/f8c4b5c6-2777-4890-82af-f3bf0c8c1181" />

*Account management interface showing multiple account types*

<img width="1592" height="894" alt="image" src="https://github.com/user-attachments/assets/615ba628-7819-47ee-878b-52285aa2f0f2" />

*Individual account view with transaction history*

### Admin Interface
<img width="1875" height="782" alt="image" src="https://github.com/user-attachments/assets/57334096-5c58-4b85-a394-88bb9b5bf14e" />

*Enhanced admin dashboard with system statistics and quick actions*
<img width="1551" height="756" alt="image" src="https://github.com/user-attachments/assets/3c831e19-58f4-4750-b9e7-9f9f546c252d" />
<img width="1436" height="423" alt="image" src="https://github.com/user-attachments/assets/266aea28-f200-4c2e-b1a5-5704159081fe" />

*Admin interface for managing transactions and user data*

### Mobile Responsive Design
<div style="display: flex; gap: 20px;">
  
  <img width="580" height="893" alt="image" src="https://github.com/user-attachments/assets/c6053ea4-b154-428b-936c-7ed9f02512ef" />
<img width="695" height="899" alt="image" src="https://github.com/user-attachments/assets/105b19a0-fa7f-4373-9a84-c6b942844773" />
<img width="680" height="882" alt="image" src="https://github.com/user-attachments/assets/1b768fbd-632b-4622-be9c-d4ba5040c769" />

</div>

*Responsive design working seamlessly across all device sizes*

### Light Mode Support
<img width="1894" height="802" alt="image" src="https://github.com/user-attachments/assets/7c31ec46-90cb-4df2-9e6e-24c031d30453" />

*Dashboard in light mode with automatic theme switching*

## 🚀 Features

### Core Financial Management
- **Multi-Account Support**: Manage checking, savings, credit card, and investment accounts
- **Transaction Tracking**: Record income, expenses, and transfers with detailed categorization
- **Real-time Balance Calculation**: Automatic balance updates with transaction processing
- **Recurring Transactions**: Set up automated recurring income and expenses
- **Payment Method Tracking**: Track transactions by payment method (cash, credit card, etc.)

### Advanced Analytics
- **Interactive Charts**: Dynamic charts showing spending patterns and trends
- **Category Analysis**: Detailed breakdown of expenses by category
- **Monthly/Yearly Reports**: Comprehensive financial reports with export capabilities
- **Budget Tracking**: Set and monitor budgets with visual progress indicators
- **Financial Goals**: Track progress toward savings and financial objectives

### User Experience
- **Modern UI/UX**: Clean, intuitive interface with smooth animations
- **Dark/Light Mode**: Automatic theme switching with user preference storage
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Real-time Updates**: Live balance updates and transaction notifications
- **Advanced Search**: Powerful search and filtering capabilities

### Security & Performance
- **User Authentication**: Secure login with password reset functionality
- **Data Isolation**: Complete separation of user financial data
- **Performance Optimized**: Efficient database queries and caching
- **Backup & Export**: Data export capabilities for backup and analysis

## 🛠️ Technology Stack

### Backend
- **Django 4.2+**: Modern Python web framework
- **PostgreSQL**: Robust database for financial data
- **Django REST Framework**: API development
- **Celery**: Asynchronous task processing
- **Redis**: Caching and session storage

### Frontend
- **HTML5/CSS3**: Modern web standards
- **JavaScript (ES6+)**: Interactive functionality
- **Chart.js**: Dynamic data visualization
- **Bootstrap 5**: Responsive UI framework
- **Font Awesome**: Icon library

### DevOps & Deployment
- **Docker**: Containerized development and deployment
- **Docker Compose**: Multi-service orchestration
- **Nginx**: Web server and reverse proxy
- **Gunicorn**: WSGI HTTP Server

## 📋 Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- PostgreSQL 13+ (for local development)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/tigerlero/financialDjango.git
cd finance-app
```

2. **Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

3. **Build and Run**
```bash
# Build and start all services
docker-compose up --build

# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec web python manage.py generate_sample_data
```

4. **Access the Application**
- **Main App**: http://localhost:8000
- **Admin Interface**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/api/docs

### Local Development Setup

1. **Python Environment**
```bash
# Create virtual environment
python -m venv finance_env
source finance_env/bin/activate  # On Windows: finance_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Create PostgreSQL database
createdb finance_app

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

3. **Development Server**
```bash
# Start development server
python manage.py runserver

# Start Celery worker (separate terminal)
celery -A finance_project worker -l info
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test categories
make test-models
make test-views
make test-api
make test-integration

# Run performance tests
make test-performance
```

### Test Coverage
![Test Coverage](screenshots/test-coverage.png)
*Comprehensive test coverage report showing 95%+ coverage*

### Testing Strategy
- **Unit Tests**: Model validation and business logic
- **Integration Tests**: Complete user workflows
- **API Tests**: REST endpoint functionality
- **Performance Tests**: Database query optimization
- **Security Tests**: Data isolation and input validation

## 📊 API Documentation

### Authentication
```bash
# Obtain JWT token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Transactions API
```bash
# Get transactions
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/transactions/

# Create transaction
curl -X POST http://localhost:8000/api/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account": 1,
    "amount": "50.00",
    "description": "Grocery shopping",
    "transaction_type": "expense",
    "category": 1
  }'
```

### Accounts API
```bash
# Get user accounts
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/accounts/

# Get account balance
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/accounts/1/balance/
```

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/finance_app

# Security
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Custom Settings
```python
# settings/local.py
from .base import *

# Development-specific settings
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance_app_dev',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🎨 UI/UX Features

### Theme Customization
<img width="1562" height="858" alt="image" src="https://github.com/user-attachments/assets/fb3be870-1a83-4ef3-8ccf-8893df1fc06d" />

*Theme customization panel with light, dark, and auto modes*


### Authentication Flow
<img width="490" height="779" alt="image" src="https://github.com/user-attachments/assets/2bf98579-5bf8-4e53-8a61-42fc80900374" />
<img width="477" height="902" alt="image" src="https://github.com/user-attachments/assets/f25bc8a8-86c3-4c33-a3a4-207b4858b9ed" />

*Secure authentication with password strength requirements*

## 🚀 Deployment

### Production Deployment
```bash
# Production build
docker-compose -f docker-compose.prod.yml up --build -d

# SSL Certificate setup
certbot --nginx -d yourdomain.com

# Database backup
docker-compose exec db pg_dump -U finance_user finance_app > backup.sql
```


## 🙏 Acknowledgments

- Django community for the excellent framework
- Chart.js for beautiful data visualizations
- Bootstrap team for responsive design components
- Font Awesome for comprehensive icon library

---


