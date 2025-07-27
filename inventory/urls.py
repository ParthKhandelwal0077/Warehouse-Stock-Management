from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from . import views

# API Router
router = DefaultRouter()
router.register(r'products', views.ProductMasterViewSet)
router.register(r'transactions', views.StockMainViewSet)
router.register(r'stock-details', views.StockDetailViewSet)
router.register(r'reports', views.InventoryReportViewSet, basename='reports')



# Separate URL patterns for API and web
api_urlpatterns = [
    path('', include(router.urls)),
]

web_urlpatterns = [
    path('', TemplateView.as_view(template_name='inventory/dashboard.html'), name='dashboard'),
    path('products/', TemplateView.as_view(template_name='inventory/products.html'), name='products'),
    path('transactions/', TemplateView.as_view(template_name='inventory/transactions.html'), name='transactions'),
    path('reports/', TemplateView.as_view(template_name='inventory/reports.html'), name='reports'),
] 