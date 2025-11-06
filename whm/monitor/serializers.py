from rest_framework import serializers
from .models import MonitoredWebsite, AlertLog, CustomUser

# --- Authentication Serializer ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'mobile', 'password')
        extra_kwargs = {'email': {'required': True}}

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

# --- Monitoring Serializers ---

class AlertLogSerializer(serializers.ModelSerializer):
    """Serializer for AlertLog (the new HealthLog)"""
    class Meta:
        model = AlertLog
        fields = '__all__'
        read_only_fields = ('website', 'timestamp')

class MonitoredWebsiteSerializer(serializers.ModelSerializer):
    # This field name must match the related_name defined in models.py (alert_logs)
    alert_logs = AlertLogSerializer(many=True, read_only=True, source='alertlog_set')

    class Meta:
        model = MonitoredWebsite
        fields = '__all__'
        read_only_fields = ('user', 'status', 'last_check', 'last_latency_ms')