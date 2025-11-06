from django.apps import AppConfig

class MonitorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitor'
    label = 'monitor'
    
    # TEMPORARILY COMMENT OUT THE READY METHOD IF IT EXISTS
    # def ready(self):
    #     import monitor.signals
    #     from django.contrib import admin
    #     admin.autodiscover()
    # Use pass instead of ready() content for now
