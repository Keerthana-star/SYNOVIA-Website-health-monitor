from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # The URL the frontend JavaScript will connect to (e.g., ws://localhost:8000/ws/dashboard/)
    re_path(r'ws/dashboard/$', consumers.LiveDashboardConsumer.as_asgi()),
]
