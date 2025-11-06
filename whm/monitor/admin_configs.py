from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, OTP, Website, AlertContact, WebsiteCheck, Alert
from .forms import CustomUserCreationForm, CustomUserChangeForm

# =================================================================
# Custom User Admin Configuration
# =================================================================

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    # Fields displayed when viewing user details
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('mobile_number', 'first_name', 'last_name', 'is_verified')}),
    )
    # Fields displayed when adding a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('mobile_number', 'first_name', 'last_name', 'email')}),
    )
    list_display = ['mobile_number', 'email', 'first_name', 'last_name', 'is_staff', 'is_verified']
    search_fields = ['mobile_number', 'email']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(OTP)


# =================================================================
# Monitoring Model Registration
# =================================================================

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'url', 'is_active', 'last_status', 'last_check_time')
    list_filter = ('is_active', 'last_status')
    search_fields = ('name', 'url')

@admin.register(AlertContact)
class AlertContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'type', 'value', 'is_active')
    list_filter = ('type', 'is_active')

@admin.register(WebsiteCheck)
class WebsiteCheckAdmin(admin.ModelAdmin):
    list_display = ('website', 'check_time', 'status_code', 'response_time', 'is_successful')
    list_filter = ('is_successful', 'status_code')
    search_fields = ('website__name', 'website__url')
    ordering = ('-check_time',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('website', 'type', 'triggered_at')
    list_filter = ('type',)
    ordering = ('-triggered_at',)
