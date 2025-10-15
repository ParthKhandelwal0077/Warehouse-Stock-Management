#!/bin/bash

# Azure Web Service startup script
set -e

echo "Starting Azure Web Service deployment..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create admin user if it doesn't exist
echo "Creating admin user..."
python manage.py create_admin

echo "Deployment completed successfully!"

# Start the application (this will be handled by Procfile in Azure)
