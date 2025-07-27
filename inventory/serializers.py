from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .models import ProductMaster, StockMain, StockDetail

class ProductMasterSerializer(serializers.ModelSerializer):
    current_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductMaster
        fields = [
            'id', 'product_code', 'product_name', 'description', 
            'category', 'unit_of_measure', 'minimum_stock_level', 
            'maximum_stock_level', 'standard_cost', 'is_active', 
            'current_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_product_code(self, value):
        """Validate product code format and uniqueness"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Product code must be at least 3 characters long."
            )
        
        # Check uniqueness on update
        if self.instance and self.instance.product_code != value:
            if ProductMaster.objects.filter(product_code=value).exists():
                raise serializers.ValidationError(
                    "Product code already exists."
                )
        elif not self.instance:
            if ProductMaster.objects.filter(product_code=value).exists():
                raise serializers.ValidationError(
                    "Product code already exists."
                )
        
        return value.upper().strip()
    
    def validate_product_name(self, value):
        """Validate product name"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Product name must be at least 3 characters long."
            )
        return value.strip()
    
    def validate_standard_cost(self, value):
        """Validate standard cost"""
        if value and value < 0:
            raise serializers.ValidationError(
                "Standard cost cannot be negative."
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        min_stock = data.get('minimum_stock_level')
        max_stock = data.get('maximum_stock_level')
        
        if min_stock and max_stock and min_stock > max_stock:
            raise serializers.ValidationError({
                'minimum_stock_level': 'Minimum stock level cannot be greater than maximum stock level.'
            })
        
        return data

class StockDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    unit_of_measure = serializers.CharField(source='product.unit_of_measure', read_only=True)
    
    class Meta:
        model = StockDetail
        fields = [
            'id', 'product', 'product_name', 'product_code', 'unit_of_measure',
            'quantity', 'unit_cost', 'total_cost', 'lot_batch_number', 
            'expiry_date', 'location', 'remarks', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_cost', 'created_at', 'updated_at']
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )
        return value
    
    def validate_unit_cost(self, value):
        """Validate unit cost"""
        if value < 0:
            raise serializers.ValidationError(
                "Unit cost cannot be negative."
            )
        return value
    
    def validate_expiry_date(self, value):
        """Validate expiry date"""
        if value and value < timezone.now().date():
            raise serializers.ValidationError(
                "Expiry date cannot be in the past."
            )
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        # Get stock_main from context or data
        stock_main = self.context.get('stock_main')
        if not stock_main and hasattr(self, 'instance') and self.instance:
            stock_main = self.instance.stock_main
        
        # Validate stock out doesn't exceed available stock
        if stock_main and stock_main.transaction_type == 'OUT':
            product = data.get('product')
            quantity = data.get('quantity')
            
            if product and quantity:
                available_stock = product.current_stock
                # If updating existing record, add back the original quantity
                if self.instance:
                    available_stock += self.instance.quantity
                
                if quantity > available_stock:
                    raise serializers.ValidationError({
                        'quantity': f'Insufficient stock. Available: {available_stock}, Requested: {quantity}'
                    })
        
        return data

class StockMainSerializer(serializers.ModelSerializer):
    stock_details = StockDetailSerializer(many=True, read_only=True)
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StockMain
        fields = [
            'id', 'transaction_id', 'transaction_date', 'transaction_type', 
            'transaction_type_display', 'reference_number', 'vendor_customer', 
            'remarks', 'status', 'status_display', 'total_amount', 'created_by', 
            'stock_details', 'created_at', 'updated_at'
        ]
        read_only_fields = ['transaction_id', 'total_amount', 'created_at', 'updated_at']
    
    def validate_transaction_date(self, value):
        """Validate transaction date"""
        if value > timezone.now():
            raise serializers.ValidationError(
                "Transaction date cannot be in the future."
            )
        return value
    
    def validate_reference_number(self, value):
        """Validate reference number"""
        if value and len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Reference number must be at least 3 characters long."
            )
        return value.strip() if value else value
    
    def validate_vendor_customer(self, value):
        """Validate vendor/customer name"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Vendor/Customer name must be at least 2 characters long."
            )
        return value.strip() if value else value

class StockMainCreateSerializer(serializers.ModelSerializer):
    stock_details = StockDetailSerializer(many=True, write_only=True)
    
    class Meta:
        model = StockMain
        fields = [
            'transaction_date', 'transaction_type', 'reference_number', 
            'vendor_customer', 'remarks', 'status', 'created_by', 'stock_details'
        ]
    
    def validate_stock_details(self, value):
        """Validate stock details"""
        if not value:
            raise serializers.ValidationError(
                "At least one stock detail is required."
            )
        
        # Check for duplicate products in the same transaction
        products = [detail['product'] for detail in value]
        if len(products) != len(set(products)):
            raise serializers.ValidationError(
                "Duplicate products are not allowed in the same transaction."
            )
        
        return value
    
    def create(self, validated_data):
        """Create stock main with details"""
        stock_details_data = validated_data.pop('stock_details')
        stock_main = StockMain.objects.create(**validated_data)
        
        for detail_data in stock_details_data:
            StockDetail.objects.create(stock_main=stock_main, **detail_data)
        
        return stock_main
    
    def to_representation(self, instance):
        """Return full representation after creation"""
        return StockMainSerializer(instance, context=self.context).data

class InventoryReportSerializer(serializers.Serializer):
    """Serializer for inventory report"""
    product_code = serializers.CharField()
    product_name = serializers.CharField()
    category = serializers.CharField()
    unit_of_measure = serializers.CharField()
    current_stock = serializers.DecimalField(max_digits=12, decimal_places=2)
    minimum_stock_level = serializers.DecimalField(max_digits=12, decimal_places=2)
    maximum_stock_level = serializers.DecimalField(max_digits=12, decimal_places=2)
    standard_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    stock_status = serializers.CharField()  # LOW, NORMAL, HIGH
    last_transaction_date = serializers.DateTimeField(allow_null=True)

class StockMovementSerializer(serializers.Serializer):
    """Serializer for stock movement report"""
    product_code = serializers.CharField()
    product_name = serializers.CharField()
    transaction_id = serializers.CharField()
    transaction_date = serializers.DateTimeField()
    transaction_type = serializers.CharField()
    transaction_type_display = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    vendor_customer = serializers.CharField(allow_null=True)
    reference_number = serializers.CharField(allow_null=True)
    running_balance = serializers.DecimalField(max_digits=12, decimal_places=2) 