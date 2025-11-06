# whm/monitor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),  # Home / SPA
    path('register/', views.api_register_user, name='api_register_user'),  # Registration endpoint
    path('verify-otp/', views.api_verify_otp, name='api_verify_otp'),    # OTP verification endpoint
    path('login/', views.api_login_user, name='api_login_user'),          # Login endpoint
    path('logout/', views.api_logout_user, name='api_logout_user'),       # Logout endpoint
    path('dashboard/', views.dashboard_view, name='dashboard_view'),      # Protected dashboard
]
