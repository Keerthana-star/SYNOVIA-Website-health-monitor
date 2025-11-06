from rest_framework import views, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer
from django.core.cache import cache
import random
import string
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token # Required for final step

# --- PLACEHOLDER FOR EXTERNAL SERVICE ---
# You need to install Twilio (pip install twilio) and configure it
def send_otp_sms(mobile_number, otp_code):
    """
    SIMULATED: Replace this with actual Twilio API call logic.
    Twilio credentials should be in settings.py
    """
    print(f"--- REAL SMS FAILED! ---")
    print(f"Simulating sending OTP: {otp_code} to {mobile_number}")
    print(f"--- REAL SMS FAILED! ---")
    # In your real code, you would use Twilio client here:
    # client.messages.create(to=mobile_number, from_='<TWILIO_NUMBER>', body=f'Your OTP is {otp_code}')
    return True # Assume success for now

class RegistrationView(views.APIView):
    """Handles initial registration and sends OTP."""
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # 1. Generate OTP and store user data temporarily
            otp_code = ''.join(random.choices(string.digits, k=6))
            temp_key = f"reg_user_{data['email']}"
            
            # Store data and OTP in cache for 5 minutes (for verification)
            cache.set(temp_key, {'data': data, 'otp': otp_code}, timeout=300) 
            
            # 2. Attempt to send OTP (simulated/placeholder)
            if not send_otp_sms(data['mobile'], otp_code):
                 return Response({"error": "Could not send OTP. Check mobile number or Twilio config."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "OTP sent successfully. Please verify."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OTPVerificationView(views.APIView):
    """Handles OTP verification and finalizes registration."""
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        temp_key = f"reg_user_{email}"
        cached_data = cache.get(temp_key)

        if not cached_data or cached_data['otp'] != otp:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 3. Create the real user
        user_data = cached_data['data']
        User.objects.create_user(
            username=email, # Use email as username for simplicity
            email=email,
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        
        # Clean up cache
        cache.delete(temp_key)
        
        # 4. Optional: Log user in immediately and return a token
        user = authenticate(username=email, password=user_data['password'])
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"message": "Registration complete.", "token": token.key}, status=status.HTTP_201_CREATED)
            
        return Response({"message": "Registration complete. Please log in."}, status=status.HTTP_201_CREATED)
