# monitor_project/wsgi.py

import os
from django.core.wsgi import get_wsgi_application

# NOTE: This setting MUST match what's in manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_project.settings')

application = get_wsgi_application()