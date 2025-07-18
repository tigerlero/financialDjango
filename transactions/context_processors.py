"""
Context processors for the transactions app
"""
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json
from .models import Account, Transaction, Category, UserPreferences


def admin_stats(request):
    """Add admin statistics to context"""
    if request.path.startswith('/admin/'):
        try:
            # Basic counts
            user_count = User.objects.count()
            account_count = Account.objects.count()
            transaction_count = Transaction.objects.count()
            category_count = Category.objects.count()
            
            # Calculate total balance
            total_balance = Account.objects.aggregate(
                total=Sum('balance')
            )['total'] or 0
            
            # Pending transactions
            pending_transactions = Transaction.objects.filter(
                status='pending'
            ).count()
            
            # Today's activity
            today = timezone.now().date()
            recent_user_count = User.objects.filter(
                date_joined__date=today
            ).count()
            
            recent_account_count = Account.objects.filter(
                created_at__date=today
            ).count()
            
            recent_transaction_count = Transaction.objects.filter(
                created_at__date=today
            ).count()
            
            # Monthly transaction data for chart
            monthly_labels = []
            monthly_transactions = []
            
            for i in range(6):
                month_start = timezone.now().replace(day=1) - timedelta(days=i*30)
                month_end = month_start + timedelta(days=30)
                
                month_count = Transaction.objects.filter(
                    created_at__gte=month_start,
                    created_at__lt=month_end
                ).count()
                
                monthly_labels.append(month_start.strftime('%b'))
                monthly_transactions.append(month_count)
            
            monthly_labels.reverse()
            monthly_transactions.reverse()
            
            # Account types distribution
            account_types = Account.objects.values('account_type').annotate(
                count=Count('id')
            ).order_by('account_type')
            
            account_type_labels = []
            account_type_data = []
            
            for account_type in account_types:
                account_type_labels.append(account_type['account_type'].title())
                account_type_data.append(account_type['count'])
            
            return {
                'user_count': user_count,
                'account_count': account_count,
                'transaction_count': transaction_count,
                'category_count': category_count,
                'total_balance': total_balance,
                'pending_transactions': pending_transactions,
                'recent_user_count': recent_user_count,
                'recent_account_count': recent_account_count,
                'recent_transaction_count': recent_transaction_count,
                'monthly_labels': json.dumps(monthly_labels),
                'monthly_transactions': json.dumps(monthly_transactions),
                'account_type_labels': json.dumps(account_type_labels),
                'account_type_data': json.dumps(account_type_data),
            }
        except Exception:
            return {}
    return {}


def user_preferences(request):
    """Add user preferences to context"""
    if request.user.is_authenticated:
        try:
            preferences = UserPreferences.get_or_create_for_user(request.user)
            return {'preferences': preferences}
        except Exception:
            # Fallback to default preferences
            return {
                'preferences': {
                    'theme': 'light',
                    'default_currency': 'USD',
                    'date_format': 'MM/DD/YYYY',
                    'language': 'en',
                    'email_notifications': True,
                    'low_balance_alerts': True,
                }
            }
    return {
        'preferences': {
            'theme': 'light',
            'default_currency': 'USD',
            'date_format': 'MM/DD/YYYY',
            'language': 'en',
            'email_notifications': True,
            'low_balance_alerts': True,
        }
    }
