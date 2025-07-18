"""
Celery tasks for asynchronous processing
"""
from celery import shared_task
import logging
from django.db import transaction
from .models import Transaction
from .services import StripePaymentService

logger = logging.getLogger(__name__)


@shared_task
def process_payment_async(transaction_id: int, payment_intent_id: str):
    """Process payment asynchronously"""
    try:
        txn = Transaction.objects.get(id=transaction_id)
        
        # Confirm payment with Stripe
        result = StripePaymentService.confirm_payment(payment_intent_id)
        
        if result['success']:
            txn.status = 'processing'
            txn.external_payment_id = payment_intent_id
            txn.save()
            
            # Complete the transaction
            txn.complete_transaction()
            
            logger.info(f"Payment processed successfully: {txn.reference_number}")
            return {'success': True, 'transaction_id': transaction_id}
        else:
            txn.status = 'failed'
            txn.metadata['error'] = result['error']
            txn.save()
            
            logger.error(f"Payment failed: {txn.reference_number} - {result['error']}")
            return {'success': False, 'error': result['error']}
            
    except Transaction.DoesNotExist:
        logger.error(f"Transaction not found: {transaction_id}")
        return {'success': False, 'error': 'Transaction not found'}
    except Exception as e:
        logger.error(f"Payment processing error: {e}")
        return {'success': False, 'error': str(e)}


@shared_task
def process_recurring_transactions():
    """Process due recurring transactions"""
    from django.utils import timezone
    from .models import RecurringTransaction
    from dateutil.relativedelta import relativedelta
    
    due_transactions = RecurringTransaction.objects.filter(
        is_active=True,
        next_transaction_date__lte=timezone.now()
    )
    
    processed = 0
    for recurring in due_transactions:
        try:
            # Create transaction
            txn = Transaction.objects.create(
                account=recurring.account,
                amount=recurring.amount,
                description=f"Recurring: {recurring.description}",
                transaction_type='debit',
                category=recurring.category,
                metadata={'recurring_id': recurring.id}
            )
            
            # Complete transaction
            txn.complete_transaction()
            
            # Update next transaction date
            if recurring.frequency == 'daily':
                recurring.next_transaction_date += timezone.timedelta(days=1)
            elif recurring.frequency == 'weekly':
                recurring.next_transaction_date += timezone.timedelta(weeks=1)
            elif recurring.frequency == 'monthly':
                recurring.next_transaction_date += relativedelta(months=1)
            elif recurring.frequency == 'quarterly':
                recurring.next_transaction_date += relativedelta(months=3)
            elif recurring.frequency == 'yearly':
                recurring.next_transaction_date += relativedelta(years=1)
            
            recurring.save()
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing recurring transaction {recurring.id}: {e}")
    
    logger.info(f"Processed {processed} recurring transactions")
    return processed


@shared_task
def generate_monthly_report(user_id: int, year: int, month: int):
    """Generate monthly financial report"""
    from django.contrib.auth.models import User
    from .models import Account
    from .services import AnalyticsService
    from datetime import datetime
    
    try:
        user = User.objects.get(id=user_id)
        accounts = Account.objects.filter(user=user, is_active=True)
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        report_data = {
            'user_id': user_id,
            'period': f"{year}-{month:02d}",
            'accounts': []
        }
        
        for account in accounts:
            spending = AnalyticsService.get_spending_by_category(
                account, start_date, end_date
            )
            
            account_data = {
                'account_id': account.id,
                'account_name': account.name,
                'balance': float(account.get_balance()),
                'spending_by_category': {k: float(v) for k, v in spending.items()}
            }
            report_data['accounts'].append(account_data)
        
        # Here you could save to database, send email, etc.
        logger.info(f"Monthly report generated for user {user_id}")
        return report_data
        
    except Exception as e:
        logger.error(f"Error generating monthly report: {e}")
        return {'error': str(e)}
