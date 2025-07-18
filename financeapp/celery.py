"""
Celery configuration for financeapp project
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')

app = Celery('financeapp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery beat schedule for recurring tasks
app.conf.beat_schedule = {
    'process-recurring-transactions': {
        'task': 'transactions.tasks.process_recurring_transactions',
        'schedule': 3600.0,  # Run every hour
    },
}

app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
