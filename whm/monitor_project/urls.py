from django.contrib import admin
from django.urls import path, include
from monitor import views as monitor_views  # Import the index_view

urlpatterns = [
    # The root URL (http://127.0.0.1:8000/) renders your single HTML file (SPA)
    path('', monitor_views.index_view, name='home'), 

    # Admin panel
    path('admin/', admin.site.urls),

    # All application-specific views and APIs are under the 'monitor/' prefix
    path('monitor/', include('monitor.urls')),
    
    # IMPORTANT: Do NOT include 'django.contrib.auth.urls' here.
]