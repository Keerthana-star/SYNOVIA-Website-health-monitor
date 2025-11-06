import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import monitor.routing # Import the routing file from your 'monitor' app

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_project.settings')

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Handle standard HTTP requests (including Django views)
    "http": django_asgi_app,
    
    # Handle WebSocket requests
    "websocket": AuthMiddlewareStack( # Use AuthMiddlewareStack to access user info in consumers
        URLRouter(
            monitor.routing.websocket_urlpatterns
        )
    ),
})
