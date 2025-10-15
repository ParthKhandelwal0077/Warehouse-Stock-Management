# Azure Deployment Troubleshooting Guide

## Current Issue: HTTP 301 Redirects

Based on your deployment logs, all requests are returning HTTP 301 redirects. Here are the fixes:

### 1. **IMMEDIATE FIXES APPLIED**

✅ **Disabled HTTPS redirects** (temporarily for debugging)
✅ **Updated ALLOWED_HOSTS** to accept all hosts
✅ **Enhanced startup script** with better logging
✅ **Improved Procfile** with better Gunicorn configuration

### 2. **REQUIRED AZURE CONFIGURATION**

**Set these environment variables in Azure Portal:**

```
SECRET_KEY=your-secret-key-here
DEBUG=False
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
ADMIN_EMAIL=admin@yourdomain.com
```

### 3. **DEBUGGING STEPS**

1. **Check Azure App Service Logs:**
   - Go to Azure Portal → Your Web App → Monitoring → Log stream
   - Look for Django startup messages

2. **Run Debug Script:**
   ```bash
   python debug_view.py
   ```

3. **Check Django Configuration:**
   ```bash
   python manage.py check --deploy
   ```

4. **Test URLs manually:**
   ```bash
   python manage.py shell
   >>> from django.test import Client
   >>> c = Client()
   >>> response = c.get('/')
   >>> print(response.status_code, response.content)
   ```

### 4. **COMMON ISSUES & SOLUTIONS**

#### Issue: HTTP 301 Redirects
**Cause:** ALLOWED_HOSTS mismatch or HTTPS redirect settings
**Solution:** 
- Ensure your Azure domain is in ALLOWED_HOSTS
- Temporarily disable SECURE_SSL_REDIRECT

#### Issue: Static Files Not Loading
**Cause:** STATIC_ROOT or WhiteNoise configuration
**Solution:**
- Verify `collectstatic` runs successfully
- Check WhiteNoise middleware is enabled

#### Issue: Database Connection Errors
**Cause:** Missing DATABASE_URL or incorrect connection string
**Solution:**
- Use SQLite for testing (default)
- Configure PostgreSQL connection string for production

### 5. **NEXT STEPS**

1. **Deploy the updated code** with the fixes
2. **Set environment variables** in Azure Portal
3. **Monitor the logs** during deployment
4. **Test the application** once deployed

### 6. **VERIFICATION CHECKLIST**

- [ ] Environment variables set in Azure
- [ ] Application starts without errors
- [ ] Root URL returns HTTP 200 (not 301)
- [ ] Static files load correctly
- [ ] Database migrations applied
- [ ] Admin user created successfully

### 7. **LOG ANALYSIS**

Your logs show:
- ✅ Dependencies installed successfully
- ✅ Static files collected (160 files)
- ✅ Gunicorn started on port 8000
- ❌ All requests return 301 redirects

The 301 redirects indicate Django is rejecting requests due to configuration issues, not application errors.

### 8. **CONTACT SUPPORT**

If issues persist after applying these fixes:
1. Share the updated deployment logs
2. Confirm environment variables are set
3. Test with the debug script output
