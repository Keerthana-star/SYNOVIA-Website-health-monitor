from django.urls import path
from django.views.generic import TemplateView

# This file handles the non-API, frontend-serving routes for the monitor app.

urlpatterns = [
    # This serves the dashboard.html template when a user navigates to the root URL (/)
    path('', TemplateView.as_view(template_name='monitor/dashboard.html'), name='dashboard'),
]
