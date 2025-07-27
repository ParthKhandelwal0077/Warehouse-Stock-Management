from django.db import models
from django.core.validators import MinValueValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
import uuid

class ProductMaster(models.Model):
    """Product Master (prodmast) - stores product details"""
    
    PRODUCT_CATEGORIES = [
        ('RAW', 'Raw Material'),
        ('WIP', 'Work in Progress'),
        ('FIN', 'Finished Goods'),
        ('CON', 'Consumables'),
    ]
    
    UNIT_CHOICES = [
        ('PCS', 'Pieces'),
        ('KG', 'Kilograms'),
        ('LTR', 'Liters'),
        ('MTR', 'Meters'),
        ('BOX', 'Boxes'),
        ('SET', 'Sets'),
    ]
    
    product_code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Unique product code"
    )
    product_name = models.CharField(
        max_length=100, 
        help_text="Product name"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Product description"
    )
    category = models.CharField(
        max_length=3, 
        choices=PRODUCT_CATEGORIES, 
        default='FIN',
        help_text="Product category"
    )
    unit_of_measure = models.CharField(
        max_length=3, 
        choices=UNIT_CHOICES, 
        default='PCS',
        help_text="Unit of measurement"
    )
    minimum_stock_level = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Minimum stock level for alerts"
    )
    maximum_stock_level = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Maximum stock level"
    )
    standard_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Standard cost per unit"
    )
    is_active = models.BooleanField(
        default=True, 
        help_text="Whether product is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'prodmast'
        verbose_name = 'Product Master'
        verbose_name_plural = 'Product Masters'
        ordering = ['product_code']
    
    def clean(self):
        """Custom validation"""
        if self.minimum_stock_level and self.maximum_stock_level:
            if self.minimum_stock_level > self.maximum_stock_level:
                raise ValidationError({
                    'minimum_stock_level': 'Minimum stock level cannot be greater than maximum stock level.'
                })
    
    def __str__(self):
        return f"{self.product_code} - {self.product_name}"
    
    @property
    def current_stock(self):
        """Calculate current stock from all transactions"""
        from django.db.models import Sum, F
        
        stock_in = StockDetail.objects.filter(
            product=self,
            stock_main__transaction_type='IN'
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        stock_out = StockDetail.objects.filter(
            product=self,
            stock_main__transaction_type='OUT'
        ).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return stock_in - stock_out

class StockMain(models.Model):
    """Stock Main (stckmain) - stores transaction header details"""
    
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
        ('TRF', 'Transfer'),
    ]
    
    TRANSACTION_STATUS = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    transaction_id = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Unique transaction ID"
    )
    transaction_date = models.DateTimeField(
        help_text="Transaction date and time"
    )
    transaction_type = models.CharField(
        max_length=3, 
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction"
    )
    reference_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="External reference number (PO, Invoice, etc.)"
    )
    vendor_customer = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Vendor or customer name"
    )
    remarks = models.TextField(
        blank=True, 
        null=True,
        help_text="Transaction remarks"
    )
    status = models.CharField(
        max_length=10, 
        choices=TRANSACTION_STATUS, 
        default='DRAFT',
        help_text="Transaction status"
    )
    total_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total transaction amount"
    )
    created_by = models.CharField(
        max_length=50, 
        default='system',
        help_text="User who created the transaction"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stckmain'
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'
        ordering = ['-transaction_date', '-created_at']
    
    def clean(self):
        """Custom validation"""
        from django.utils import timezone
        
        if self.transaction_date and self.transaction_date > timezone.now():
            raise ValidationError({
                'transaction_date': 'Transaction date cannot be in the future.'
            })
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate unique transaction ID
            from django.utils import timezone
            import random
            
            date_prefix = timezone.now().strftime('%Y%m%d')
            random_suffix = str(random.randint(1000, 9999))
            self.transaction_id = f"TXN{date_prefix}{random_suffix}"
            
            # Ensure uniqueness
            while StockMain.objects.filter(transaction_id=self.transaction_id).exists():
                random_suffix = str(random.randint(1000, 9999))
                self.transaction_id = f"TXN{date_prefix}{random_suffix}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()} ({self.transaction_date.strftime('%Y-%m-%d')})"

class StockDetail(models.Model):
    """Stock Detail (stckdetail) - stores product details within each transaction"""
    
    stock_main = models.ForeignKey(
        StockMain, 
        on_delete=models.CASCADE, 
        related_name='stock_details',
        help_text="Reference to stock main transaction"
    )
    product = models.ForeignKey(
        ProductMaster, 
        on_delete=models.CASCADE, 
        related_name='stock_details',
        help_text="Product reference"
    )
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Transaction quantity"
    )
    unit_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost per unit"
    )
    total_cost = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total cost (quantity * unit_cost)"
    )
    lot_batch_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Lot or batch number"
    )
    expiry_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Product expiry date"
    )
    location = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        help_text="Storage location"
    )
    remarks = models.TextField(
        blank=True, 
        null=True,
        help_text="Line item remarks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stckdetail'
        verbose_name = 'Stock Detail'
        verbose_name_plural = 'Stock Details'
        ordering = ['stock_main', 'product']
        unique_together = [['stock_main', 'product', 'lot_batch_number']]
    
    def clean(self):
        """Custom validation"""
        from django.utils import timezone
        
        if self.expiry_date and self.expiry_date < timezone.now().date():
            raise ValidationError({
                'expiry_date': 'Expiry date cannot be in the past.'
            })
        
        # Validate stock out doesn't exceed available stock
        if self.stock_main and self.stock_main.transaction_type == 'OUT':
            if self.product:
                available_stock = self.product.current_stock
                if self.quantity > available_stock:
                    raise ValidationError({
                        'quantity': f'Insufficient stock. Available: {available_stock}, Requested: {self.quantity}'
                    })
    
    def save(self, *args, **kwargs):
        # Calculate total cost
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)
        
        # Update stock main total
        if self.stock_main:
            total = self.stock_main.stock_details.aggregate(
                total=models.Sum('total_cost')
            )['total'] or 0
            self.stock_main.total_amount = total
            self.stock_main.save()
    
    def __str__(self):
        return f"{self.stock_main.transaction_id} - {self.product.product_code} ({self.quantity})" 