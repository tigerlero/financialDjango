"""
Views for transaction management with API endpoints
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import json
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Account, Transaction, Category, UserPreferences
from .serializers import (
    AccountSerializer, TransactionSerializer, CategorySerializer
)
from .services import TransactionService, AnalyticsService

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.ModelViewSet):
    """API ViewSet for accounts"""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get current account balance"""
        account = self.get_object()
        return Response({
            'balance': account.get_balance(),
            'currency': account.currency
        })
    
    @action(detail=True, methods=['get'])
    def spending_by_category(self, request, pk=None):
        """Get spending breakdown by category"""
        account = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        spending = AnalyticsService.get_spending_by_category(
            account, start_date, end_date
        )
        
        return Response({
            'spending_by_category': {k: float(v) for k, v in spending.items()}
        })


class TransactionViewSet(viewsets.ModelViewSet):
    """API ViewSet for transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = Transaction.objects.filter(
            account__user=self.request.user
        ).select_related('account', 'category', 'to_account')
        
        # Filter by account
        account_id = self.request.query_params.get('account_id')
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(description__icontains=search) |
                Q(reference_number__icontains=search)
            )
        
        return queryset.order_by('-transaction_date')
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Create a payment transaction"""
        try:
            data = request.data
            account = get_object_or_404(
                Account, 
                id=data.get('account_id'),
                user=request.user
            )
            
            result = TransactionService.process_payment(
                account=account,
                amount=Decimal(data.get('amount')),
                payment_method_id=data.get('payment_method_id'),
                description=data.get('description')
            )
            
            if result['success']:
                return Response({
                    'success': True,
                    'transaction_id': result['transaction_id'],
                    'client_secret': result['client_secret']
                })
            else:
                return Response(
                    {'error': result['error']},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Payment creation error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """Transfer funds between accounts"""
        try:
            data = request.data
            from_account = get_object_or_404(
                Account,
                id=data.get('from_account_id'),
                user=request.user
            )
            to_account = get_object_or_404(
                Account,
                id=data.get('to_account_id'),
                user=request.user
            )
            
            transaction = TransactionService.transfer_funds(
                from_account=from_account,
                to_account=to_account,
                amount=Decimal(data.get('amount')),
                description=data.get('description')
            )
            
            serializer = self.get_serializer(transaction)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Transfer error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """API ViewSet for categories"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.filter(is_active=True)


# Traditional Django views for frontend
@login_required
def dashboard(request):
    """Main dashboard view"""
    accounts = Account.objects.filter(user=request.user, is_active=True)
    recent_transactions = Transaction.objects.filter(
        account__user=request.user
    ).select_related('account', 'category')[:10]
    
    total_balance = sum(account.get_balance() for account in accounts)
    
    context = {
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'total_balance': total_balance,
    }
    return render(request, 'transactions/dashboard.html', context)


@login_required
def account_list(request):
    """Account list view"""
    accounts = Account.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    
    # Calculate totals
    total_balance = sum(account.get_balance() for account in accounts)
    account_count = accounts.count()
    average_balance = total_balance / account_count if account_count > 0 else 0
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'average_balance': average_balance,
    }
    return render(request, 'transactions/account_list.html', context)


@login_required
def account_detail(request, account_id):
    """Account detail view"""
    account = get_object_or_404(Account, id=account_id, user=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-transaction_date')[:50]
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'account': account,
        'transactions': page_obj,
        'current_balance': account.get_balance(),
    }
    return render(request, 'transactions/account_detail.html', context)


@login_required
def transaction_detail_ajax(request, transaction_id):
    """AJAX endpoint for transaction details"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        transaction = get_object_or_404(
            Transaction.objects.select_related('account', 'category', 'to_account'),
            id=transaction_id,
            account__user=request.user
        )
        
        # Format transaction data
        data = {
            'id': transaction.id,
            'reference_number': transaction.reference_number,
            'description': transaction.description,
            'amount': str(transaction.amount),
            'transaction_type': transaction.get_transaction_type_display(),
            'status': transaction.get_status_display(),
            'transaction_date': transaction.transaction_date.strftime('%B %d, %Y at %I:%M %p'),
            'created_at': transaction.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'account': {
                'name': transaction.account.name,
                'type': transaction.account.get_account_type_display(),
                'number': transaction.account.account_number
            },
            'category': {
                'name': transaction.category.name if transaction.category else 'Uncategorized',
                'color': transaction.category.color if transaction.category else '#6c757d'
            },
            'to_account': {
                'name': transaction.to_account.name if transaction.to_account else None,
                'type': transaction.to_account.get_account_type_display() if transaction.to_account else None
            } if transaction.to_account else None,
            'notes': transaction.notes or 'No additional notes'
        }
        
        return JsonResponse({'success': True, 'transaction': data})
        
    except Exception as e:
        logger.error(f"Transaction detail error: {e}")
        return JsonResponse({'error': 'Failed to fetch transaction details'}, status=500)


@login_required
def transaction_complete_ajax(request, transaction_id):
    """AJAX endpoint for completing a transaction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        transaction = get_object_or_404(
            Transaction,
            id=transaction_id,
            account__user=request.user,
            status='pending'  # Only pending transactions can be completed
        )
        
        # Update transaction status
        transaction.status = 'completed'
        transaction.save()
        
        logger.info(f"Transaction {transaction.reference_number} completed by user {request.user.username}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Transaction {transaction.reference_number} has been completed.',
            'new_status': 'completed'
        })
        
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found or cannot be completed'}, status=404)
    except Exception as e:
        logger.error(f"Transaction completion error: {e}")
        return JsonResponse({'error': 'Failed to complete transaction'}, status=500)


@login_required
def transaction_cancel_ajax(request, transaction_id):
    """AJAX endpoint for cancelling a transaction"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        transaction = get_object_or_404(
            Transaction,
            id=transaction_id,
            account__user=request.user,
            status__in=['pending', 'processing']  # Only pending/processing transactions can be cancelled
        )
        
        # Update transaction status
        transaction.status = 'cancelled'
        transaction.save()
        
        logger.info(f"Transaction {transaction.reference_number} cancelled by user {request.user.username}")
        
        return JsonResponse({
            'success': True, 
            'message': f'Transaction {transaction.reference_number} has been cancelled.',
            'new_status': 'cancelled'
        })
        
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found or cannot be cancelled'}, status=404)
    except Exception as e:
        logger.error(f"Transaction cancellation error: {e}")
        return JsonResponse({'error': 'Failed to cancel transaction'}, status=500)


@login_required
def transaction_export(request):
    """Export transactions to CSV or PDF"""
    from django.http import HttpResponse
    import csv
    import io
    from datetime import datetime
    
    export_format = request.GET.get('format', 'csv')
    
    # Get user's transactions
    transactions = Transaction.objects.filter(
        account__user=request.user
    ).select_related('account', 'category', 'to_account').order_by('-transaction_date')
    
    if export_format == 'csv':
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="transactions_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Date', 'Reference', 'Description', 'Account', 'Category', 
            'Amount', 'Type', 'Status', 'To Account', 'Notes'
        ])
        
        for txn in transactions:
            writer.writerow([
                txn.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
                txn.reference_number,
                txn.description,
                txn.account.name,
                txn.category.name if txn.category else 'Uncategorized',
                f"{'-' if txn.transaction_type == 'debit' else '+'}{txn.amount}",
                txn.get_transaction_type_display(),
                txn.get_status_display(),
                txn.to_account.name if txn.to_account else '',
                txn.notes or ''
            ])
        
        return response
    
    elif export_format == 'pdf':
        # For now, return CSV format - PDF would require additional libraries
        return JsonResponse({'error': 'PDF export not yet implemented. Please use CSV format.'}, status=501)
    
    else:
        return JsonResponse({'error': 'Invalid export format'}, status=400)


@login_required
def transfer_funds_ajax(request):
    """AJAX endpoint for transferring funds between accounts"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        from_account_id = data.get('from_account_id')
        to_account_id = data.get('to_account_id')
        amount = data.get('amount')
        description = data.get('description', 'Fund Transfer')
        
        # Validate inputs
        if not all([from_account_id, to_account_id, amount]):
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        try:
            amount = Decimal(str(amount))
            if amount <= 0:
                return JsonResponse({'error': 'Amount must be greater than 0'}, status=400)
        except (ValueError, InvalidOperation):
            return JsonResponse({'error': 'Invalid amount'}, status=400)
        
        # Get accounts
        from_account = get_object_or_404(Account, id=from_account_id, user=request.user)
        to_account = get_object_or_404(Account, id=to_account_id, user=request.user)
        
        # Check if accounts are different
        if from_account.id == to_account.id:
            return JsonResponse({'error': 'Cannot transfer to the same account'}, status=400)
        
        # Check sufficient balance
        if from_account.get_balance() < amount:
            return JsonResponse({'error': 'Insufficient balance'}, status=400)
        
        # Create debit transaction (outgoing)
        debit_txn = Transaction.objects.create(
            account=from_account,
            description=f"{description} to {to_account.name}",
            amount=amount,
            transaction_type='debit',
            status='completed',
            to_account=to_account
        )
        
        # Create credit transaction (incoming)
        credit_txn = Transaction.objects.create(
            account=to_account,
            description=f"{description} from {from_account.name}",
            amount=amount,
            transaction_type='credit',
            status='completed'
        )
        
        logger.info(f"Transfer completed: {amount} from {from_account.name} to {to_account.name} by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully transferred ${amount} from {from_account.name} to {to_account.name}',
            'from_balance': str(from_account.get_balance()),
            'to_balance': str(to_account.get_balance())
        })
        
    except Account.DoesNotExist:
        return JsonResponse({'error': 'Account not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Transfer error: {e}")
        return JsonResponse({'error': 'Transfer failed'}, status=500)


@login_required
def transaction_list(request):
    """Transaction list view"""
    transactions = Transaction.objects.filter(
        account__user=request.user
    ).select_related('account', 'category', 'to_account').order_by('-transaction_date')
    
    # Filter by account if specified
    account_id = request.GET.get('account')
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    
    # Filter by status if specified
    status = request.GET.get('status')
    if status:
        transactions = transactions.filter(status=status)
    
    # Filter by type if specified
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        transactions = transactions.filter(
            Q(description__icontains=search) |
            Q(reference_number__icontains=search)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user accounts for filter dropdown
    user_accounts = Account.objects.filter(user=request.user, is_active=True)
    
    context = {
        'transactions': page_obj,
        'user_accounts': user_accounts,
        'current_filters': {
            'account': account_id,
            'status': status,
            'type': transaction_type,
            'search': search,
        }
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
@require_http_methods(["GET"])
def transaction_search(request):
    """AJAX endpoint for transaction search"""
    query = request.GET.get('q', '')
    account_id = request.GET.get('account_id')
    
    transactions = Transaction.objects.filter(account__user=request.user)
    
    if query:
        transactions = transactions.filter(
            Q(description__icontains=query) |
            Q(reference_number__icontains=query)
        )
    
    if account_id:
        transactions = transactions.filter(account_id=account_id)
    
    transactions = transactions.select_related('account', 'category')[:20]
    
    data = []
    for txn in transactions:
        data.append({
            'id': txn.id,
            'description': txn.description,
            'amount': float(txn.amount),
            'transaction_type': txn.transaction_type,
            'status': txn.status,
            'date': txn.transaction_date.strftime('%Y-%m-%d %H:%M'),
            'account': txn.account.name,
            'category': txn.category.name if txn.category else None,
        })
    
    return JsonResponse({'transactions': data})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def quick_transaction(request):
    """AJAX endpoint for quick transaction creation"""
    try:
        data = json.loads(request.body)
        account = get_object_or_404(
            Account, 
            id=data.get('account_id'),
            user=request.user
        )
        
        category = None
        if data.get('category_id'):
            category = get_object_or_404(Category, id=data.get('category_id'))
        
        transaction = TransactionService.create_transaction(
            account=account,
            amount=Decimal(data.get('amount')),
            description=data.get('description'),
            transaction_type=data.get('transaction_type', 'debit'),
            category=category
        )
        
        # Auto-complete for demo purposes
        if transaction.transaction_type == 'credit':
            transaction.complete_transaction()
        
        return JsonResponse({
            'success': True,
            'transaction_id': transaction.id,
            'reference_number': transaction.reference_number,
            'new_balance': float(account.get_balance())
        })
        
    except Exception as e:
        logger.error(f"Quick transaction error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def analytics(request):
    """Analytics dashboard view"""
    accounts = Account.objects.filter(user=request.user, is_active=True)
    
    # Get analytics data
    total_balance = sum(account.get_balance() for account in accounts)
    total_transactions = Transaction.objects.filter(account__user=request.user).count()
    
    # Monthly spending/income data for charts
    import calendar
    
    # Get last 12 months data
    now = timezone.now()
    monthly_data = []
    
    for i in range(12):
        month_start = now.replace(day=1) - timedelta(days=i*30)
        month_end = month_start + timedelta(days=30)
        
        monthly_income = Transaction.objects.filter(
            account__user=request.user,
            transaction_type='credit',
            status='completed',
            transaction_date__gte=month_start,
            transaction_date__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_spending = Transaction.objects.filter(
            account__user=request.user,
            transaction_type='debit',
            status='completed',
            transaction_date__gte=month_start,
            transaction_date__lt=month_end
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'income': float(monthly_income),
            'spending': float(monthly_spending)
        })
    
    monthly_data.reverse()
    
    # Category spending
    category_spending = {}
    for account in accounts:
        spending = AnalyticsService.get_spending_by_category(
            account, 
            (now - timedelta(days=30)).date(),
            now.date()
        )
        for category, amount in spending.items():
            category_spending[category] = category_spending.get(category, 0) + float(amount)
    
    import json
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'total_transactions': total_transactions,
        'monthly_data': json.dumps(monthly_data),
        'category_spending': json.dumps(category_spending),
    }
    return render(request, 'transactions/analytics.html', context)


@login_required
def settings(request):
    """User settings view"""
    if request.method == 'POST':
        # Handle account settings update
        if 'update_account' in request.POST:
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.save()
            
            messages.success(request, 'Account settings updated successfully!')
            return JsonResponse({'success': True, 'message': 'Account settings updated successfully!'})
        
        # Handle password change
        elif 'change_password' in request.POST:
            from django.contrib.auth import update_session_auth_hash
            from django.contrib.auth.forms import PasswordChangeForm
            
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return JsonResponse({'success': True, 'message': 'Password changed successfully!'})
            else:
                errors = []
                for field, error_list in form.errors.items():
                    for error in error_list:
                        errors.append(f"{field}: {error}")
                return JsonResponse({'success': False, 'errors': errors})
        
        # Handle preferences update
        elif 'update_preferences' in request.POST:
            preferences = UserPreferences.get_or_create_for_user(request.user)
            preferences.default_currency = request.POST.get('default_currency', 'USD')
            preferences.date_format = request.POST.get('date_format', 'MM/DD/YYYY')
            preferences.language = request.POST.get('language', 'en')
            preferences.theme = request.POST.get('theme', 'light')
            preferences.email_notifications = request.POST.get('email_notifications') == 'on'
            preferences.low_balance_alerts = request.POST.get('low_balance_alerts') == 'on'
            preferences.save()
            
            messages.success(request, 'Preferences updated successfully!')
            return JsonResponse({'success': True, 'message': 'Preferences updated successfully!'})
    
    # Get or create user preferences
    try:
        preferences = UserPreferences.get_or_create_for_user(request.user)
    except Exception as e:
        # Fallback to default preferences if there's an issue
        preferences = type('DefaultPreferences', (), {
            'default_currency': 'USD',
            'date_format': 'MM/DD/YYYY',
            'language': 'en',
            'theme': 'light',
            'email_notifications': True,
            'low_balance_alerts': True,
        })()
    
    context = {
        'user': request.user,
        'preferences': preferences,
    }
    return render(request, 'transactions/settings.html', context)


@login_required
def profile(request):
    """User profile view"""
    accounts = Account.objects.filter(user=request.user, is_active=True)
    recent_transactions = Transaction.objects.filter(
        account__user=request.user
    ).select_related('account', 'category')[:10]
    
    context = {
        'user': request.user,
        'accounts': accounts,
        'recent_transactions': recent_transactions,
        'total_balance': sum(account.get_balance() for account in accounts),
    }
    return render(request, 'transactions/profile.html', context)


@login_required
def notifications(request):
    """User notifications view"""
    # For now, we'll create some sample notifications
    # In a real app, these would come from a notifications system
    sample_notifications = [
        {
            'id': 1,
            'title': 'Account Balance Low',
            'message': 'Your checking account balance is below $100',
            'type': 'warning',
            'timestamp': timezone.now() - timedelta(hours=2),
            'read': False
        },
        {
            'id': 2,
            'title': 'Transaction Completed',
            'message': 'Your transfer of $500 has been completed',
            'type': 'success',
            'timestamp': timezone.now() - timedelta(hours=5),
            'read': True
        },
        {
            'id': 3,
            'title': 'Monthly Statement Ready',
            'message': 'Your monthly statement is now available',
            'type': 'info',
            'timestamp': timezone.now() - timedelta(days=1),
            'read': False
        }
    ]
    
    context = {
        'notifications': sample_notifications,
    }
    return render(request, 'transactions/notifications.html', context)
