from rest_framework import serializers
from django.contrib.auth.models import User

class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for handling user registration data from the frontend.
    """
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    mobile = serializers.CharField(max_length=15) # Assuming E.164 format
    password = serializers.CharField(write_only=True)
    
    # We will use this to store temporary data during registration
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
