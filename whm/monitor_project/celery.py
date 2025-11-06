# monitor_project/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_project.settings')

app = Celery('monitor_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery settings should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Celery Beat Settings (The Scheduler)
app.conf.beat_schedule = {
    'run-all-checks-every-60-seconds': {
        'task': 'monitor.tasks.run_all_checks',
        'schedule': 60.0, # Run every 60 seconds
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')