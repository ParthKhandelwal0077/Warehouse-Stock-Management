#!/usr/bin/env bash
# Azure Web Service build script
# Exit on error
set -o errexit

echo "Starting Azure build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Convert static asset files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Apply any outstanding database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create admin user automatically
echo "Creating admin user..."
python manage.py create_admin

echo "Build process completed successfully!" 