# Finance Management Application

A comprehensive Django-based personal finance management system with modern UI, real-time analytics, and robust financial tracking capabilities.

## 📸 Application Screenshots

### Dashboard Overview
![Dashboard Screenshot](<img width="1884" height="885" alt="image" src="https://github.com/user-attachments/assets/85ed6a08-b1f5-4b81-aea8-03daf772a9e0" />

)
*Main dashboard showing account balances, recent transactions, and quick actions*

### Transaction Management
![Transaction List](screenshots/transactions-list.png)
*Transaction listing with filtering and search capabilities*

![Add Transaction](screenshots/add-transaction.png)
*Transaction creation form with category selection and validation*

### Analytics & Reports
![Analytics Dashboard](screenshots/analytics.png)
*Interactive charts showing spending patterns and financial trends*

![Monthly Reports](screenshots/monthly-reports.png)
*Detailed monthly financial reports with category breakdowns*

### Account Management
![Account Overview](screenshots/accounts.png)
*Account management interface showing multiple account types*

![Account Details](screenshots/account-details.png)
*Individual account view with transaction history*

### Admin Interface
![Admin Dashboard](screenshots/admin-dashboard.png)
*Enhanced admin dashboard with system statistics and quick actions*

![Admin Transaction Management](screenshots/admin-transactions.png)
*Admin interface for managing transactions and user data*

### Mobile Responsive Design
<div style="display: flex; gap: 20px;">
  <img src="screenshots/mobile-dashboard.png" alt="Mobile Dashboard" width="300">
  <img src="screenshots/mobile-transactions.png" alt="Mobile Transactions" width="300">
  <img src="screenshots/mobile-analytics.png" alt="Mobile Analytics" width="300">
</div>

*Responsive design working seamlessly across all device sizes*

### Dark Mode Support
![Dark Mode Dashboard](screenshots/dark-mode-dashboard.png)
*Dashboard in dark mode with automatic theme switching*

![Dark Mode Analytics](screenshots/dark-mode-analytics.png)
*Analytics page with dark theme for better night viewing*

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
git clone https://github.com/yourusername/finance-app.git
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

## 📱 Mobile App Screenshots

### iOS Interface
<div style="display: flex; gap: 10px;">
  <img src="screenshots/ios-dashboard.png" alt="iOS Dashboard" width="200">
  <img src="screenshots/ios-transactions.png" alt="iOS Transactions" width="200">
  <img src="screenshots/ios-analytics.png" alt="iOS Analytics" width="200">
  <img src="screenshots/ios-settings.png" alt="iOS Settings" width="200">
</div>

### Android Interface
<div style="display: flex; gap: 10px;">
  <img src="screenshots/android-dashboard.png" alt="Android Dashboard" width="200">
  <img src="screenshots/android-transactions.png" alt="Android Transactions" width="200">
  <img src="screenshots/android-analytics.png" alt="Android Analytics" width="200">
  <img src="screenshots/android-settings.png" alt="Android Settings" width="200">
</div>

## 🎨 UI/UX Features

### Theme Customization
![Theme Settings](screenshots/theme-settings.png)
*Theme customization panel with light, dark, and auto modes*

### Accessibility Features
![Accessibility](screenshots/accessibility.png)
*High contrast mode and keyboard navigation support*

### Animation Showcase
![Animations](screenshots/animations.gif)
*Smooth transitions and micro-interactions throughout the app*

## 📈 Performance Metrics

### Load Testing Results
![Performance Metrics](screenshots/performance-metrics.png)
*Application performance under various load conditions*

### Database Optimization
![Database Performance](screenshots/db-performance.png)
*Query optimization results and response times*

## 🔐 Security Features

### Authentication Flow
![Login Process](screenshots/login-flow.png)
*Secure authentication with password strength requirements*

### Data Encryption
![Security Dashboard](screenshots/security-dashboard.png)
*Security settings and data protection features*

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

### Monitoring Dashboard
![Monitoring](screenshots/monitoring-dashboard.png)
*System monitoring with metrics and alerts*

## 🤝 Contributing

### Development Workflow
![Development Process](screenshots/development-workflow.png)
*Git workflow and contribution guidelines*

### Code Quality
![Code Quality](screenshots/code-quality.png)
*Code coverage and quality metrics*

## 📞 Support & Documentation

### Help Center
![Help Center](screenshots/help-center.png)
*In-app help system with tutorials and FAQs*

### API Documentation
![API Docs](screenshots/api-documentation.png)
*Interactive API documentation with examples*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Chart.js for beautiful data visualizations
- Bootstrap team for responsive design components
- Font Awesome for comprehensive icon library

---

## 📁 Screenshot Directory Structure

To properly display all screenshots, organize them in the following structure:

```
screenshots/
├── dashboard.png
├── transactions-list.png
├── add-transaction.png
├── analytics.png
├── monthly-reports.png
├── accounts.png
├── account-details.png
├── admin-dashboard.png
├── admin-transactions.png
├── mobile-dashboard.png
├── mobile-transactions.png
├── mobile-analytics.png
├── dark-mode-dashboard.png
├── dark-mode-analytics.png
├── test-coverage.png
├── ios-dashboard.png
├── ios-transactions.png
├── ios-analytics.png
├── ios-settings.png
├── android-dashboard.png
├── android-transactions.png
├── android-analytics.png
├── android-settings.png
├── theme-settings.png
├── accessibility.png
├── animations.gif
├── performance-metrics.png
├── db-performance.png
├── login-flow.png
├── security-dashboard.png
├── monitoring-dashboard.png
├── development-workflow.png
├── code-quality.png
├── help-center.png
└── api-documentation.png
```

## 📝 Screenshot Guidelines

### Taking Screenshots
1. **Resolution**: Use 1920x1080 for desktop screenshots
2. **Mobile**: Use actual device screenshots (375x812 for iPhone, 360x640 for Android)
3. **Quality**: Save as PNG for UI screenshots, GIF for animations
4. **Consistency**: Use the same browser and zoom level for all screenshots
5. **Content**: Include realistic sample data, avoid lorem ipsum

### Screenshot Checklist
- [ ] Dashboard with sample financial data
- [ ] Transaction list with various transaction types
- [ ] Add/Edit transaction forms
- [ ] Analytics charts with real data
- [ ] Account management interface
- [ ] Admin dashboard with statistics
- [ ] Mobile responsive views
- [ ] Dark mode variations
- [ ] Error states and validation messages
- [ ] Loading states and animations

This README structure provides comprehensive visual documentation of your finance application, making it easy for users, contributors, and stakeholders to understand the application's capabilities and interface design.
