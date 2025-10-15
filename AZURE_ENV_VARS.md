# Azure Environment Variables Configuration

Add these environment variables to your Azure Web App:

**Go to Azure Portal → Your Web App → Configuration → Application Settings**

## Required Environment Variables

```
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=False
DJANGO_SETTINGS_MODULE=warehouse_system.settings
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password
ADMIN_EMAIL=admin@yourdomain.com
WEBSITE_HOSTNAME=your-app-name.azurewebsites.net
PORT=8000
```

## Optional Environment Variables

```
DATABASE_URL=postgresql://username:password@hostname:port/database_name
DJANGO_LOG_LEVEL=INFO
PYTHONPATH=/home/site/wwwroot
```

## Important Notes

1. **SECRET_KEY**: Generate a new secret key for production
2. **DEBUG**: Must be False in production
3. **ADMIN_PASSWORD**: Change the default password
4. **WEBSITE_HOSTNAME**: Replace with your actual Azure Web App URL
5. **DATABASE_URL**: Only needed if using PostgreSQL database

## Generate Secret Key

Run this Python command to generate a new secret key:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
