#!/bin/bash

# Azure Web Service startup script
set -e

echo "=== Starting Azure Web Service deployment ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Django version: $(python -c 'import django; print(django.get_version())')"

# Install dependencies
echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

# Check Django setup
echo "=== Checking Django configuration ==="
python manage.py check --deploy

# Collect static files
echo "=== Collecting static files ==="
python manage.py collectstatic --noinput --verbosity=2

# Apply database migrations
echo "=== Applying database migrations ==="
python manage.py migrate --verbosity=2

# Create admin user if it doesn't exist
echo "=== Creating admin user ==="
python manage.py create_admin

echo "=== Deployment completed successfully! ==="

# Start the application (this will be handled by Procfile in Azure)
