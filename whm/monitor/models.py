from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid
import logging

logger = logging.getLogger(__name__)

# =================================================================
# Custom User Manager (Required by AbstractBaseUser)
# =================================================================

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where mobile_number is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, mobile_number, password=None, **extra_fields):
        """
        Creates and saves a regular User with the given mobile number and password.
        """
        if not mobile_number:
            raise ValueError('The Mobile Number field must be set')
        
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password, **extra_fields):
        """
        Creates and saves a superuser with the given mobile number and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True) # Superusers are verified by default

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(mobile_number, password, **extra_fields)

# =================================================================
# Custom User Model (Required by AUTH_USER_MODEL)
# =================================================================

class CustomUser(AbstractBaseUser, PermissionsMixin):
    mobile_number = models.CharField(unique=True, max_length=15)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'custom_user'


    def get_full_name(self):
        """Returns the first_name plus the last_name, with a space in between."""
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        """Returns the short name for the user."""
        return self.first_name

# Class definitions needed by tasks.py
class Website(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='websites')
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    http_method = models.CharField(
        max_length=10,
        choices=[('GET', 'GET'), ('POST', 'POST')],
        default='GET'
    )
    last_checked = models.DateTimeField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    is_up = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.url})"


class CheckResult(models.Model):
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status_code = models.IntegerField()
    response_time_ms = models.FloatField(null=True, blank=True)
    is_up = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.website.url} - {self.timestamp.date()}"


class AlertContact(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='alert_contacts')
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # ✅ added field

    def __str__(self):
        return f"AlertContact for {self.user.email or self.phone_number}"
