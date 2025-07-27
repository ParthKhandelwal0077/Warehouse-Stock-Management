"""
WSGI config for warehouse_system project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'warehouse_system.settings')

application = get_wsgi_application() 