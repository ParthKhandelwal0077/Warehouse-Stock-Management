#!/usr/bin/env python3

import datetime
import os
import sys
import traceback

if __name__ == '__main__':
    # Azure Web Service Python handler
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        # Import Django WSGI application
        from warehouse_system.wsgi import application
        
        # Set up Django
        import django
        from django.core.wsgi import get_wsgi_application
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_system.settings')
        django.setup()
        
        # Get the WSGI application
        application = get_wsgi_application()
        
    except Exception as e:
        # Log any import errors
        print(f"Error importing Django application: {e}")
        traceback.print_exc()
        raise
