from django.contrib import admin
from django.utils.html import format_html
from .models import ProductMaster, StockMain, StockDetail

@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = [
        'product_code', 
        'product_name', 
        'category', 
        'unit_of_measure', 
        'current_stock_display',
        'minimum_stock_level', 
        'is_active'
    ]
    list_filter = ['category', 'unit_of_measure', 'is_active', 'created_at']
    search_fields = ['product_code', 'product_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['product_code']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_code', 'product_name', 'description', 'category')
        }),
        ('Stock Management', {
            'fields': ('unit_of_measure', 'minimum_stock_level', 'maximum_stock_level', 'standard_cost')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def current_stock_display(self, obj):
        stock = obj.current_stock
        if stock < obj.minimum_stock_level:
            return format_html(
                '<span style="color: red; font-weight: bold;">{}</span>',
                stock
            )
        return stock
    current_stock_display.short_description = 'Current Stock'

class StockDetailInline(admin.TabularInline):
    model = StockDetail
    extra = 1
    readonly_fields = ['total_cost', 'created_at', 'updated_at']
    fields = [
        'product', 
        'quantity', 
        'unit_cost', 
        'total_cost', 
        'lot_batch_number', 
        'location', 
        'remarks'
    ]

@admin.register(StockMain)
class StockMainAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 
        'transaction_date', 
        'transaction_type', 
        'status', 
        'vendor_customer', 
        'total_amount',
        'created_by'
    ]
    list_filter = [
        'transaction_type', 
        'status', 
        'transaction_date', 
        'created_at'
    ]
    search_fields = [
        'transaction_id', 
        'reference_number', 
        'vendor_customer'
    ]
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-transaction_date', '-created_at']
    inlines = [StockDetailInline]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'transaction_id', 
                'transaction_date', 
                'transaction_type', 
                'status'
            )
        }),
        ('Reference Details', {
            'fields': (
                'reference_number', 
                'vendor_customer', 
                'remarks'
            )
        }),
        ('Financial Information', {
            'fields': ('total_amount',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StockDetail)
class StockDetailAdmin(admin.ModelAdmin):
    list_display = [
        'stock_main', 
        'product', 
        'quantity', 
        'unit_cost', 
        'total_cost', 
        'location'
    ]
    list_filter = [
        'stock_main__transaction_type', 
        'product__category', 
        'location',
        'created_at'
    ]
    search_fields = [
        'stock_main__transaction_id', 
        'product__product_code', 
        'product__product_name',
        'lot_batch_number'
    ]
    readonly_fields = ['total_cost', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Transaction Reference', {
            'fields': ('stock_main', 'product')
        }),
        ('Quantity and Cost', {
            'fields': ('quantity', 'unit_cost', 'total_cost')
        }),
        ('Additional Details', {
            'fields': (
                'lot_batch_number', 
                'expiry_date', 
                'location', 
                'remarks'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Customize admin site
admin.site.site_header = "Warehouse Inventory Management"
admin.site.site_title = "Warehouse Admin"
admin.site.index_title = "Welcome to Warehouse Inventory Management System" 