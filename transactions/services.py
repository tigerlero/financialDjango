"""
Service layer for handling complex business logic and third-party integrations
"""
import stripe
import logging
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from typing import Dict, Any, Optional
from .models import Transaction, Account, PaymentMethod
# Removed circular import - will import in method

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Handle Stripe payment processing"""
    
    @staticmethod
    def create_payment_intent(amount: Decimal, currency: str = 'usd', 
                            metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a Stripe payment intent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=metadata or {}
            )
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
        """Confirm a payment intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent.status == 'succeeded':
                return {
                    'success': True,
                    'status': intent.status,
                    'payment_method': intent.payment_method
                }
            return {
                'success': False,
                'status': intent.status,
                'error': 'Payment not successful'
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe confirmation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_customer(user_id: int, email: str) -> Dict[str, Any]:
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={'user_id': user_id}
            )
            return {
                'success': True,
                'customer_id': customer.id
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe customer creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class TransactionService:
    """Business logic for transaction processing"""
    
    @staticmethod
    @transaction.atomic
    def create_transaction(account: Account, amount: Decimal, 
                         description: str, transaction_type: str = 'debit',
                         category=None, metadata: Dict[str, Any] = None) -> Transaction:
        """Create a new transaction with proper validation"""
        
        # Validate transaction
        if transaction_type == 'debit' and not account.can_debit(amount):
            raise ValueError("Insufficient funds")
        
        # Create transaction
        txn = Transaction.objects.create(
            account=account,
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            category=category,
            metadata=metadata or {}
        )
        
        logger.info(f"Transaction created: {txn.reference_number}")
        return txn
    
    @staticmethod
    @transaction.atomic
    def process_payment(account: Account, amount: Decimal, 
                       payment_method_id: str, description: str) -> Dict[str, Any]:
        """Process a payment using Stripe"""
        
        # Create payment intent
        result = StripePaymentService.create_payment_intent(
            amount=amount,
            metadata={
                'account_id': account.id,
                'user_id': account.user.id
            }
        )
        
        if not result['success']:
            return result
        
        # Create pending transaction
        txn = TransactionService.create_transaction(
            account=account,
            amount=amount,
            description=description,
            transaction_type='debit',
            metadata={
                'payment_intent_id': result['payment_intent_id'],
                'payment_method': payment_method_id
            }
        )
        
        # Process payment asynchronously
        from .tasks import process_payment_async
        process_payment_async.delay(txn.id, result['payment_intent_id'])
        
        return {
            'success': True,
            'transaction_id': txn.id,
            'client_secret': result['client_secret']
        }
    
    @staticmethod
    @transaction.atomic
    def transfer_funds(from_account: Account, to_account: Account, 
                      amount: Decimal, description: str) -> Transaction:
        """Transfer funds between accounts"""
        
        if not from_account.can_debit(amount):
            raise ValueError("Insufficient funds in source account")
        
        # Create transfer transaction
        txn = Transaction.objects.create(
            account=from_account,
            to_account=to_account,
            amount=amount,
            description=description,
            transaction_type='transfer'
        )
        
        # Process the transfer
        txn.complete_transaction()
        
        logger.info(f"Transfer completed: {txn.reference_number}")
        return txn


class AnalyticsService:
    """Financial analytics and reporting"""
    
    @staticmethod
    def get_spending_by_category(account: Account, start_date, end_date) -> Dict[str, Decimal]:
        """Get spending breakdown by category"""
        from django.db.models import Sum
        
        transactions = Transaction.objects.filter(
            account=account,
            transaction_type='debit',
            status='completed',
            transaction_date__range=[start_date, end_date]
        ).select_related('category')
        
        spending = {}
        for txn in transactions:
            category_name = txn.category.name if txn.category else 'Uncategorized'
            spending[category_name] = spending.get(category_name, Decimal('0.00')) + txn.amount
        
        return spending
    
    @staticmethod
    def get_monthly_trends(account: Account, months: int = 6) -> Dict[str, Dict[str, Decimal]]:
        """Get monthly spending and income trends"""
        from django.db.models import Sum
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        
        end_date = timezone.now()
        start_date = end_date - relativedelta(months=months)
        
        transactions = Transaction.objects.filter(
            account=account,
            status='completed',
            transaction_date__range=[start_date, end_date]
        ).extra(
            select={'month': "DATE_TRUNC('month', transaction_date)"}
        ).values('month', 'transaction_type').annotate(
            total=Sum('amount')
        ).order_by('month')
        
        trends = {}
        for item in transactions:
            month_key = item['month'].strftime('%Y-%m')
            if month_key not in trends:
                trends[month_key] = {'income': Decimal('0.00'), 'spending': Decimal('0.00')}
            
            if item['transaction_type'] == 'credit':
                trends[month_key]['income'] += item['total']
            else:
                trends[month_key]['spending'] += item['total']
        
        return trends
