# Warehouse Inventory Management System

A comprehensive warehouse inventory management system built with Django and Django REST Framework. This system provides complete stock tracking, transaction management, and reporting capabilities for small to medium warehouses.

## Features

### Core Functionality
- **Product Management**: Complete CRUD operations for product master data
- **Stock Transactions**: Handle stock in, stock out, adjustments, and transfers
- **Real-time Inventory**: Track current stock levels with automatic calculations
- **Low Stock Alerts**: Automated alerts when products fall below minimum levels
- **Comprehensive Reporting**: Current inventory, stock movements, and analytics

### Technical Features
- **Clean API Design**: RESTful APIs with comprehensive validation
- **Modern UI**: Bootstrap-based responsive web interface
- **Data Validation**: Extensive input validation at model and API levels
- **Stock Level Enforcement**: Prevents negative stock and overselling
- **Transaction Integrity**: Database transactions ensure data consistency

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5.1.3, Vanilla JavaScript
- **API**: RESTful APIs with proper HTTP status codes
- **Documentation**: Auto-generated API documentation

## Project Structure

```
warehouse_system/
├── warehouse_system/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── inventory/                  # Main inventory app
│   ├── models.py              # Database models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── admin.py               # Django admin configuration
│   └── urls.py                # URL routing
├── templates/                  # HTML templates
│   ├── base.html
│   └── inventory/
│       ├── dashboard.html
│       ├── products.html
│       ├── transactions.html
│       └── reports.html
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Database Schema

### Product Master (prodmast)
- Product code, name, description
- Category (Raw Material, WIP, Finished Goods, Consumables)
- Unit of measure, stock levels, costs
- Active/inactive status

### Stock Main (stckmain)
- Transaction header information
- Transaction type (IN/OUT/ADJ/TRF)
- Date, reference, vendor/customer
- Status (Draft, Pending, Completed, Cancelled)

### Stock Detail (stckdetail)
- Line items for each transaction
- Product, quantity, costs
- Lot/batch tracking, expiry dates
- Storage location information

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Database Setup
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

### Step 3: Run the Development Server
```bash
python manage.py runserver
```

The system will be available at:
- **Web Interface**: http://127.0.0.1:8000/
- **API Documentation**: http://127.0.0.1:8000/api/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Usage Guide

### 1. Product Management
- Navigate to **Products** section
- Add products with codes, names, categories, and stock levels
- Set minimum/maximum stock levels for alerts
- Define standard costs for valuation

### 2. Stock Transactions
- Use **Transactions** section to record stock movements
- **Stock In**: Purchases, receipts, production
- **Stock Out**: Sales, issues, consumption
- **Adjustments**: Cycle counts, corrections
- **Transfers**: Location movements

### 3. Inventory Monitoring
- **Dashboard**: Real-time overview and alerts
- **Reports**: Detailed inventory and movement reports
- **Low Stock Alerts**: Automatic monitoring and notifications

### 4. API Integration
All functionality is available via REST APIs:
```bash
# Get all products
GET /api/products/

# Create stock transaction
POST /api/transactions/
{
  "transaction_type": "IN",
  "transaction_date": "2023-12-01T10:00:00",
  "stock_details": [
    {
      "product": 1,
      "quantity": 100,
      "unit_cost": 10.50
    }
  ]
}

# Get current inventory report
GET /api/reports/current_inventory/

# Get low stock alerts
GET /api/products/low_stock_alert/
```

## Data Validation

The system implements comprehensive validation:

### Product Validation
- Unique product codes (auto-converted to uppercase)
- Product names minimum 3 characters
- Non-negative stock levels and costs
- Min level ≤ Max level validation

### Transaction Validation
- Transaction dates cannot be in future
- Stock out quantities checked against available stock
- Duplicate products prevented in same transaction
- Automatic transaction ID generation

### Stock Level Enforcement
- Prevents negative stock levels
- Real-time stock calculation from all transactions
- Automatic alerts for low stock situations

## API Documentation

### Product Endpoints
- `GET /api/products/` - List all products
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product
- `GET /api/products/low_stock_alert/` - Get low stock products
- `GET /api/products/{id}/stock_movements/` - Get product movement history

### Transaction Endpoints
- `GET /api/transactions/` - List all transactions
- `POST /api/transactions/` - Create new transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `POST /api/transactions/{id}/complete_transaction/` - Complete transaction
- `POST /api/transactions/{id}/cancel_transaction/` - Cancel transaction
- `GET /api/transactions/transaction_summary/` - Get transaction summary

### Report Endpoints
- `GET /api/reports/current_inventory/` - Current inventory report
- `GET /api/reports/stock_movement_report/` - Stock movement report
- `GET /api/reports/dashboard_stats/` - Dashboard statistics

## Security Features

- Input validation and sanitization
- SQL injection prevention via Django ORM
- XSS protection with template escaping
- CSRF protection for web forms
- Comprehensive error handling

## Customization

### Adding New Transaction Types
1. Update `TRANSACTION_TYPES` in `models.py`
2. Update validation logic in `serializers.py`
3. Add frontend handling in templates

### Extending Product Categories
1. Update `PRODUCT_CATEGORIES` in `models.py`
2. Update frontend dropdowns in templates

### Custom Validations
1. Add business rules in model `clean()` methods
2. Extend serializer validation methods
3. Add API endpoint validations

## Production Deployment

### Database Configuration
For production, update `settings.py` for PostgreSQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'warehouse_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Security Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-production-secret-key'
```

### Static Files
```bash
python manage.py collectstatic
```

## Troubleshooting

### Common Issues

1. **Migration Errors**
   ```bash
   python manage.py migrate --fake-initial
   ```

2. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --clear
   ```

3. **API 404 Errors**
   - Check URL configuration in `urls.py`
   - Verify API base URL in frontend JavaScript

4. **Validation Errors**
   - Check model validations in `models.py`
   - Review serializer validation in `serializers.py`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is built for educational and commercial use. Please review the license terms before deployment.

## Support

For technical support or questions:
- Check the Django documentation: https://docs.djangoproject.com/
- Review Django REST Framework docs: https://www.django-rest-framework.org/
- Submit issues via the project repository

---

**Built with Django & Django REST Framework**
*A modern, scalable solution for warehouse inventory management* 