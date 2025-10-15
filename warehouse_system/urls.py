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
# if debug is true it indicates the the development server will be serving static files from the static root directory but if false these url patterns are not used and the static files are served by the web server which in this case we are using whitenoise . Django in production don't serve static files due to performance reason
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 