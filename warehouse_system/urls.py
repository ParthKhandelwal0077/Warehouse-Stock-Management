"""
URL configuration for warehouse_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from inventory.urls import api_urlpatterns, web_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_urlpatterns)),
    path('', include(web_urlpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 