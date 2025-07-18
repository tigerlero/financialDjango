#!/usr/bin/env python
"""
Test runner script for the finance app
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financeapp.settings')
    django.setup()
    
    # Run tests with coverage
    import subprocess
    
    # Run pytest with coverage
    cmd = [
        'python', '-m', 'pytest',
        '--cov=transactions',
        '--cov-report=html',
        '--cov-report=term-missing',
        '-v'
    ]
    
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])
    
    subprocess.run(cmd)
