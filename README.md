# Django Finance App

A comprehensive financial management system built with Django, PostgreSQL, and modern web technologies.

## Features

### 🏦 Account Management
- Multiple account types (checking, savings, credit, investment)
- Real-time balance calculations
- Account-specific transaction history
- Multi-currency support

### 💳 Transaction Processing
- Secure payment processing with Stripe integration
- Fund transfers between accounts
- Recurring transaction support
- Transaction categorization and search
- Real-time AJAX updates

### 📊 Analytics & Reporting
- Spending breakdown by category
- Monthly trends and insights
- Visual charts and graphs
- Automated monthly reports

### 🔧 Technical Features
- RESTful API endpoints
- Responsive Bootstrap UI
- Docker containerization
- Comprehensive test coverage
- Celery async task processing
- Redis caching

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5, Chart.js, jQuery
- **Payments**: Stripe API
- **Caching**: Redis
- **Task Queue**: Celery
- **Testing**: pytest, pytest-django
- **Containerization**: Docker, Docker Compose

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your Stripe keys and other settings
   ```

3. Start the application:
   ```bash
   docker-compose up --build
   ```

4. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the application at `http://localhost:8000`

## 🌐 Application URLs

- **Landing Page**: http://localhost:8000 (for unauthenticated users)
- **Login**: http://localhost:8000/login/
- **Register**: http://localhost:8000/register/
- **Dashboard**: http://localhost:8000/dashboard/ (requires authentication)
- **Admin Panel**: http://localhost:8000/admin/

## 🔐 Authentication

The application now includes a complete authentication system:

- **Landing Page**: Modern landing page with features overview
- **User Registration**: Create new accounts with form validation
- **User Login**: Secure login with demo credentials available
- **Dashboard**: Protected dashboard for authenticated users
- **Logout**: Secure logout functionality

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up PostgreSQL database
3. Configure environment variables in `.env`
4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Accounts
- `GET /api/accounts/` - List user accounts
- `POST /api/accounts/` - Create new account
- `GET /api/accounts/{id}/` - Get account details
- `GET /api/accounts/{id}/balance/` - Get current balance
- `GET /api/accounts/{id}/spending_by_category/` - Get spending analysis

### Transactions
- `GET /api/transactions/` - List transactions
- `POST /api/transactions/` - Create transaction
- `POST /api/transactions/create_payment/` - Process payment
- `POST /api/transactions/transfer/` - Transfer funds

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category

## Testing

Run the comprehensive test suite:

```bash
# Using pytest
python -m pytest

# With coverage
python -m pytest --cov=transactions --cov-report=html

# Run specific test types
python -m pytest -m unit
python -m pytest -m integration
python -m pytest -m api
```

### Test Coverage

- **Unit Tests**: Model logic, services, tasks
- **Integration Tests**: API endpoints, views
- **Functional Tests**: User workflows
- **Performance Tests**: Database queries, API response times

## Architecture

### Models
- `Account`: Bank accounts with balance tracking
- `Transaction`: Financial transactions with audit trail
- `Category`: Transaction categorization
- `RecurringTransaction`: Automated recurring payments
- `PaymentMethod`: Stored payment methods

### Services
- `TransactionService`: Business logic for transactions
- `StripePaymentService`: Payment processing
- `AnalyticsService`: Financial analytics and reporting

### Tasks (Celery)
- `process_payment_async`: Async payment processing
- `process_recurring_transactions`: Scheduled recurring payments
- `generate_monthly_report`: Automated reporting

## Key Features Demonstrated

### 1. Django + PostgreSQL
- Complex financial models with proper constraints
- Optimized queries with select_related and prefetch_related
- Database indexes for performance
- Proper handling of decimal precision for financial data

### 2. API Integration
- Stripe payment processing
- RESTful API design
- Proper error handling and validation
- Async task processing with Celery

### 3. Frontend + AJAX
- Responsive Bootstrap UI
- Real-time updates with AJAX
- Interactive charts and dashboards
- Form validation and user feedback

### 4. Docker + Testing
- Complete Docker Compose setup
- Comprehensive test coverage (unit, integration, API)
- Automated testing with pytest
- Coverage reporting

## Challenges Solved

### Financial Data Handling
- Proper decimal precision for monetary values
- Transaction atomicity and consistency
- Balance calculations and validation
- Multi-currency support

### Performance Optimization
- Database query optimization
- Efficient pagination
- Caching strategies
- Background task processing

### Security
- CSRF protection
- User authentication and authorization
- Input validation and sanitization
- Secure payment processing

## Environment Variables

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/1
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLIC_KEY=pk_test_...
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details
