from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# If your forms.py exists and defines CustomUserCreationForm / CustomUserChangeForm, import them
try:
    from .forms import CustomUserCreationForm, CustomUserChangeForm
except ImportError:
    CustomUserCreationForm = None
    CustomUserChangeForm = None

# =================================================================
# Custom User Admin Configuration
# =================================================================
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    fieldsets = (
        (None, {'fields': ('mobile_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile_number', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_verified', 'is_staff', 'is_superuser'),
        }),
    )

    list_display = ['mobile_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_verified']
    search_fields = ['mobile_number', 'email']
    ordering = ['mobile_number']

# =================================================================
# Optional: Register other models if they exist
# =================================================================
optional_models = [
    'OTP', 'Website', 'WebsiteCheck', 'Alert', 'AlertContact', 'AlertHistory'
]

for model_name in optional_models:
    try:
        model = getattr(__import__('monitor.models', fromlist=[model_name]), model_name)
        admin.site.register(model)
    except Exception:
        # Skip if the model is not defined yet
        pass
from django.contrib.auth.models import Group # Import the default Group model

# Unregister the Group model to hide it from the admin index
admin.site.unregister(Group)