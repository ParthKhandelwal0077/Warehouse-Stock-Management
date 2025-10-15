#!/usr/bin/env python3
"""
Debug script to test Django setup
Run this to check if Django is working properly
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_system.settings')

try:
    django.setup()
    
    print("✅ Django setup successful!")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    print(f"Database: {settings.DATABASES['default']['ENGINE']}")
    
    # Test URL resolution
    from django.urls import reverse
    from django.test import Client
    
    client = Client()
    
    # Test root URL
    try:
        response = client.get('/')
        print(f"✅ Root URL status: {response.status_code}")
    except Exception as e:
        print(f"❌ Root URL error: {e}")
    
    # Test admin URL
    try:
        response = client.get('/admin/')
        print(f"✅ Admin URL status: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin URL error: {e}")
        
    print("✅ Debug check completed!")
    
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    import traceback
    traceback.print_exc()
