import random
import json
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError

# Assuming these imports exist and are correct in your monitor/ directory
from .forms import CustomUserCreationForm 
from django.http import HttpResponse

def index_view(request):
    return HttpResponse("Welcome to the Website Health Monitor!")

#from .models import CustomUser, OTP 

# --- Mock SMS Function (OTP generation for console output) ---
def send_otp_via_mock_sms(mobile_number, otp_code):
    """ Mocks sending an OTP to the console for verification. """
    print(f"\n=============================================")
    print(f"--- OTP SENT TO {mobile_number} ---")
    print(f"OTP CODE: {otp_code}")
    print(f"=============================================\n")
    return True

# --- 1. View to serve the single HTML file (Your entire frontend) ---
def index_view(request):
    """Serves the single-page application (SPA) template (monitor/templates/index.html)."""
    # **NOTE: Ensure your frontend code is in monitor/templates/index.html**
    return render(request, 'monitor/dashboard.html')

# --- 2. API Endpoint for User Registration (Handles OTP generation) ---
@csrf_exempt 
def api_register_user(request):
    if request.method == 'POST':
        # Load JSON data from the request body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

        # Your form expects mobile_number, password, first_name, last_name, email
        form = CustomUserCreationForm(data)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Set initial state for verification
                user.is_active = False 
                user.is_verified = False 
                user.username = user.mobile_number # Use mobile number as username
                user.save()

                # --- OTP Generation and Storage ---
                otp_code = str(random.randint(100000, 999999))
                # Update or create the OTP for this user, resetting the created_at time
                OTP.objects.update_or_create(user=user, defaults={'otp_code': otp_code})
                
                send_otp_via_mock_sms(user.mobile_number, otp_code)
                
                # Success response that triggers the frontend to show the OTP page
                return JsonResponse({
                    'success': True,
                    'message': 'Registration successful. OTP sent to mobile.',
                    'mobile_number': user.mobile_number 
                }, status=201)

            except IntegrityError:
                return JsonResponse({'error': 'This mobile number is already registered.'}, status=409)
            except Exception as e:
                print(f"Registration error: {e}")
                return JsonResponse({'error': 'An unexpected server error occurred.'}, status=500)
        else:
            # Return detailed form errors
            return JsonResponse({'error': form.errors}, status=400)
    
    return JsonResponse({'error': 'Method not allowed.'}, status=405)


# --- 3. API Endpoint for OTP Verification (Activates the user) ---
@csrf_exempt
def api_verify_otp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile_number = data.get('mobile_number')
            entered_otp = data.get('otp_code')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Missing mobile_number or otp_code in request.'}, status=400)

        try:
            user = CustomUser.objects.get(mobile_number=mobile_number)
            otp_obj = OTP.objects.get(user=user)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found.'}, status=404)
        except OTP.DoesNotExist:
            return JsonResponse({'error': 'OTP record not found. Please re-register.'}, status=400)

        # Assuming your OTP model has an is_expired() method to check the timestamp
        if hasattr(otp_obj, 'is_expired') and otp_obj.is_expired():
             return JsonResponse({'error': "OTP has expired. Please request a new one."}, status=400)

        if entered_otp == otp_obj.otp_code:
            # Activation logic
            user.is_active = True
            user.is_verified = True
            user.save()
            otp_obj.delete() # OTP is single-use
            
            # Log in the user immediately after successful verification
            login(request, user)

            return JsonResponse({'success': True, 'message': 'Verification successful! You are now logged in.'})
        else:
            return JsonResponse({'error': "Invalid OTP code. Please try again."}, status=401)
    
    return JsonResponse({'error': 'Method not allowed.'}, status=405)


# --- 4. API Endpoint for User Login ---
@csrf_exempt
def api_login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mobile_number = data.get('mobile_number')
            password = data.get('password')
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({'error': 'Missing mobile number or password.'}, status=400)
        
        # Authenticate using mobile_number and password
        user = authenticate(request, username=mobile_number, password=password) 

        if user is not None:
            if user.is_verified:
                login(request, user)
                return JsonResponse({'success': True, 'message': 'Login successful.', 'user_id': user.id})
            else:
                # If user exists but is not verified, prompt re-verification
                return JsonResponse({'error': 'Account not verified. Please verify your mobile number.'}, status=403) 
        else:
            return JsonResponse({'error': 'Invalid mobile number or password.'}, status=401)
    
    return JsonResponse({'error': 'Method not allowed.'}, status=405)


# --- 5. API Endpoint for User Logout ---
def api_logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        return JsonResponse({'success': True, 'message': 'Logged out successfully.'})
    return JsonResponse({'success': True, 'message': 'No user was logged in.'})

# --- 6. Dummy Protected Dashboard View (For frontend to check session status) ---
@login_required
def dashboard_view(request):
    """ Used by the frontend to confirm the user is logged in and verified. """
    if not request.user.is_verified:
        return JsonResponse({'error': 'User not verified.'}, status=403)
        
    return JsonResponse({'message': 'Session is valid.', 'user_id': request.user.id}, status=200)