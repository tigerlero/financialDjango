"""
URL patterns for transactions app
"""
from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    # Authentication URLs
    path('', auth_views.landing_page, name='landing'),
    path('login/', auth_views.login_view, name='login'),
    path('register/', auth_views.register_view, name='register'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('ajax/quick-register/', auth_views.quick_register, name='quick_register'),
    
    # Dashboard and main app URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('accounts/', views.account_list, name='account_list'),
    path('accounts/<int:account_id>/', views.account_detail, name='account_detail'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('ajax/transaction-search/', views.transaction_search, name='transaction_search'),
    path('ajax/quick-transaction/', views.quick_transaction, name='quick_transaction'),
    path('ajax/transaction-detail/<int:transaction_id>/', views.transaction_detail_ajax, name='transaction_detail_ajax'),
    path('ajax/transaction-complete/<int:transaction_id>/', views.transaction_complete_ajax, name='transaction_complete_ajax'),
    path('ajax/transaction-cancel/<int:transaction_id>/', views.transaction_cancel_ajax, name='transaction_cancel_ajax'),
    path('ajax/transfer-funds/', views.transfer_funds_ajax, name='transfer_funds_ajax'),
    path('export/transactions/', views.transaction_export, name='transaction_export'),
    
    # User pages
    path('analytics/', views.analytics, name='analytics'),
    path('settings/', views.settings, name='settings'),
    path('profile/', views.profile, name='profile'),
    path('notifications/', views.notifications, name='notifications'),
]
