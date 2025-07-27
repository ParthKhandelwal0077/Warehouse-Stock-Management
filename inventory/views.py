from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Max, F, Case, When, Value, CharField
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import ProductMaster, StockMain, StockDetail
from .serializers import (
    ProductMasterSerializer, StockMainSerializer, StockDetailSerializer,
    StockMainCreateSerializer, InventoryReportSerializer, StockMovementSerializer
)

class ProductMasterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Product Master records
    Provides CRUD operations and inventory-related reports
    """
    queryset = ProductMaster.objects.all()
    serializer_class = ProductMasterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'unit_of_measure', 'is_active']
    search_fields = ['product_code', 'product_name', 'description']
    ordering_fields = ['product_code', 'product_name', 'created_at', 'current_stock']
    ordering = ['product_code']
    
    @action(detail=False, methods=['get'])
    def low_stock_alert(self, request):
        """Get products with stock below minimum level"""
        low_stock_products = []
        
        for product in self.get_queryset().filter(is_active=True):
            current_stock = product.current_stock
            if current_stock < product.minimum_stock_level:
                low_stock_products.append({
                    'id': product.id,
                    'product_code': product.product_code,
                    'product_name': product.product_name,
                    'current_stock': current_stock,
                    'minimum_stock_level': product.minimum_stock_level,
                    'shortage': product.minimum_stock_level - current_stock
                })
        
        return Response({
            'count': len(low_stock_products),
            'products': low_stock_products
        })
    
    @action(detail=True, methods=['get'])
    def stock_movements(self, request, pk=None):
        """Get stock movement history for a specific product"""
        product = self.get_object()
        
        movements = StockDetail.objects.filter(
            product=product
        ).select_related('stock_main').order_by('-stock_main__transaction_date')
        
        # Calculate running balance
        running_balance = Decimal('0')
        movement_data = []
        
        for movement in reversed(movements):
            if movement.stock_main.transaction_type == 'IN':
                running_balance += movement.quantity
            elif movement.stock_main.transaction_type == 'OUT':
                running_balance -= movement.quantity
            elif movement.stock_main.transaction_type == 'ADJ':
                # For adjustments, assume quantity represents the adjustment amount
                running_balance += movement.quantity
            
            movement_data.append({
                'product_code': product.product_code,
                'product_name': product.product_name,
                'transaction_id': movement.stock_main.transaction_id,
                'transaction_date': movement.stock_main.transaction_date,
                'transaction_type': movement.stock_main.transaction_type,
                'transaction_type_display': movement.stock_main.get_transaction_type_display(),
                'quantity': movement.quantity,
                'unit_cost': movement.unit_cost,
                'total_cost': movement.total_cost,
                'vendor_customer': movement.stock_main.vendor_customer,
                'reference_number': movement.stock_main.reference_number,
                'running_balance': running_balance
            })
        
        # Reverse to show latest first
        movement_data.reverse()
        
        serializer = StockMovementSerializer(movement_data, many=True)
        return Response({
            'product': ProductMasterSerializer(product).data,
            'movements': serializer.data
        })

class StockMainViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Stock Transactions
    Provides CRUD operations for stock movements
    """
    queryset = StockMain.objects.all().prefetch_related('stock_details__product')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['transaction_type', 'status', 'created_by']
    search_fields = ['transaction_id', 'reference_number', 'vendor_customer']
    ordering_fields = ['transaction_date', 'created_at', 'total_amount']
    ordering = ['-transaction_date', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StockMainCreateSerializer
        return StockMainSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create new stock transaction with validation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Additional business logic validation
        transaction_type = serializer.validated_data.get('transaction_type')
        stock_details = serializer.validated_data.get('stock_details', [])
        
        # Validate stock availability for OUT transactions
        if transaction_type == 'OUT':
            for detail in stock_details:
                product = detail['product']
                quantity = detail['quantity']
                current_stock = product.current_stock
                
                if quantity > current_stock:
                    return Response({
                        'error': f'Insufficient stock for product {product.product_code}. '
                                f'Available: {current_stock}, Requested: {quantity}'
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['post'])
    def complete_transaction(self, request, pk=None):
        """Mark transaction as completed"""
        transaction_obj = self.get_object()
        
        if transaction_obj.status == 'COMPLETED':
            return Response({
                'error': 'Transaction is already completed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        transaction_obj.status = 'COMPLETED'
        transaction_obj.save()
        
        serializer = self.get_serializer(transaction_obj)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel_transaction(self, request, pk=None):
        """Cancel transaction"""
        transaction_obj = self.get_object()
        
        if transaction_obj.status == 'COMPLETED':
            return Response({
                'error': 'Cannot cancel completed transaction'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        transaction_obj.status = 'CANCELLED'
        transaction_obj.save()
        
        serializer = self.get_serializer(transaction_obj)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def transaction_summary(self, request):
        """Get transaction summary for dashboard"""
        today = timezone.now().date()
        
        # Get date range from query params
        start_date = request.query_params.get('start_date', today - timedelta(days=30))
        end_date = request.query_params.get('end_date', today)
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        queryset = self.get_queryset().filter(
            transaction_date__date__range=[start_date, end_date]
        )
        
        summary = {
            'total_transactions': queryset.count(),
            'stock_in_transactions': queryset.filter(transaction_type='IN').count(),
            'stock_out_transactions': queryset.filter(transaction_type='OUT').count(),
            'adjustment_transactions': queryset.filter(transaction_type='ADJ').count(),
            'total_value': queryset.aggregate(total=Sum('total_amount'))['total'] or 0,
            'pending_transactions': queryset.filter(status='PENDING').count(),
            'completed_transactions': queryset.filter(status='COMPLETED').count(),
        }
        
        return Response(summary)

class StockDetailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Stock Detail records
    """
    queryset = StockDetail.objects.all().select_related('stock_main', 'product')
    serializer_class = StockDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock_main__transaction_type', 'product__category', 'location']
    search_fields = ['product__product_code', 'product__product_name', 'lot_batch_number']
    ordering_fields = ['created_at', 'quantity', 'unit_cost']
    ordering = ['-created_at']

class InventoryReportViewSet(viewsets.ViewSet):
    """
    ViewSet for inventory reports and analytics
    """
    
    @action(detail=False, methods=['get'])
    def current_inventory(self, request):
        """Get current inventory report with stock levels and values"""
        products = ProductMaster.objects.filter(is_active=True)
        
        inventory_data = []
        for product in products:
            current_stock = product.current_stock
            stock_value = current_stock * product.standard_cost
            
            # Determine stock status
            if current_stock < product.minimum_stock_level:
                stock_status = 'LOW'
            elif current_stock > product.maximum_stock_level:
                stock_status = 'HIGH'
            else:
                stock_status = 'NORMAL'
            
            # Get last transaction date
            last_transaction = StockDetail.objects.filter(
                product=product
            ).select_related('stock_main').order_by('-stock_main__transaction_date').first()
            
            inventory_data.append({
                'product_code': product.product_code,
                'product_name': product.product_name,
                'category': product.get_category_display(),
                'unit_of_measure': product.get_unit_of_measure_display(),
                'current_stock': current_stock,
                'minimum_stock_level': product.minimum_stock_level,
                'maximum_stock_level': product.maximum_stock_level,
                'standard_cost': product.standard_cost,
                'stock_value': stock_value,
                'stock_status': stock_status,
                'last_transaction_date': last_transaction.stock_main.transaction_date if last_transaction else None
            })
        
        # Apply filters
        category = request.query_params.get('category')
        if category:
            inventory_data = [item for item in inventory_data if product.category == category]
        
        stock_status_filter = request.query_params.get('stock_status')
        if stock_status_filter:
            inventory_data = [item for item in inventory_data if item['stock_status'] == stock_status_filter]
        
        serializer = InventoryReportSerializer(inventory_data, many=True)
        return Response({
            'total_products': len(inventory_data),
            'total_stock_value': sum(item['stock_value'] for item in inventory_data),
            'low_stock_count': len([item for item in inventory_data if item['stock_status'] == 'LOW']),
            'inventory': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def stock_movement_report(self, request):
        """Get stock movement report for a date range"""
        # Get date range from query params
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        product_code = request.query_params.get('product_code')
        
        if not start_date or not end_date:
            return Response({
                'error': 'start_date and end_date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build queryset
        queryset = StockDetail.objects.filter(
            stock_main__transaction_date__date__range=[start_date, end_date]
        ).select_related('stock_main', 'product').order_by('product__product_code', 'stock_main__transaction_date')
        
        if product_code:
            queryset = queryset.filter(product__product_code=product_code)
        
        # Process movements
        movements = []
        for movement in queryset:
            movements.append({
                'product_code': movement.product.product_code,
                'product_name': movement.product.product_name,
                'transaction_id': movement.stock_main.transaction_id,
                'transaction_date': movement.stock_main.transaction_date,
                'transaction_type': movement.stock_main.transaction_type,
                'transaction_type_display': movement.stock_main.get_transaction_type_display(),
                'quantity': movement.quantity,
                'unit_cost': movement.unit_cost,
                'total_cost': movement.total_cost,
                'vendor_customer': movement.stock_main.vendor_customer,
                'reference_number': movement.stock_main.reference_number,
                'running_balance': 0  # This would need to be calculated properly
            })
        
        serializer = StockMovementSerializer(movements, many=True)
        return Response({
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            },
            'total_movements': len(movements),
            'movements': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get dashboard statistics"""
        total_products = ProductMaster.objects.filter(is_active=True).count()
        total_transactions = StockMain.objects.count()
        
        # Low stock products
        low_stock_count = 0
        total_stock_value = Decimal('0')
        
        for product in ProductMaster.objects.filter(is_active=True):
            current_stock = product.current_stock
            if current_stock < product.minimum_stock_level:
                low_stock_count += 1
            total_stock_value += current_stock * product.standard_cost
        
        # Recent transactions (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        recent_transactions = StockMain.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        # Pending transactions
        pending_transactions = StockMain.objects.filter(status='PENDING').count()
        
        return Response({
            'total_products': total_products,
            'total_transactions': total_transactions,
            'low_stock_count': low_stock_count,
            'total_stock_value': total_stock_value,
            'recent_transactions': recent_transactions,
            'pending_transactions': pending_transactions
        }) 