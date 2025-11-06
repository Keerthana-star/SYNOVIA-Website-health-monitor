# monitor/alerts.py (Final Correct Version)

import logging
from django.conf import settings
from django.core.mail import send_mail # For Django Email
from twilio.rest import Client # For Twilio SMS
from django.utils import timezone 
logger = logging.getLogger(__name__)

# --- 1. HELPER FUNCTIONS (To resolve the "is not defined" error) ---

def send_email_alert(recipient_email, subject, message_body):
    """Handles sending email alerts using Django's core mail functionality."""
    try:
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        logger.info(f"Email alert SUCCESS: Sent to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Email alert FAILURE to {recipient_email}: {e}")
        return False

def send_twilio_sms(to_number, message_body):
    """Handles sending SMS alerts using the Twilio API."""
    
    # Check for required Twilio settings (loaded from your .env file)
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    twilio_number = settings.TWILIO_PHONE_NUMBER
    
    if not all([account_sid, auth_token, twilio_number]):
        logger.error("Twilio SMS FAILURE: Credentials incomplete (check .env file).")
        return False

    try:
        client = Client(account_sid, auth_token)
        client.messages.create(
            to=to_number,
            from_=twilio_number,
            body=message_body
        )
        logger.info(f"Twilio SMS SUCCESS: Sent to {to_number}")
        return True
    except Exception as e:
        logger.error(f"Twilio SMS FAILURE to {to_number}: {e}")
        return False


# --- 2. MAIN DISPATCH FUNCTION (Accepts the required 'trigger_type' argument) ---

def dispatch_priority_alerts(website, trigger_type='DOWN_CRITICAL'):
    """
    Determines alert recipients and dispatches email/SMS based on settings.
    This function is called by monitor/tasks.py.
    """
    
    # --- Data and Recipient Retrieval (Assuming user is related to website) ---
    recipient_email = getattr(website.user, 'email', None) 

# Safely get the phone_number. If the 'phone_number' field is missing from the User model,
# it defaults to None and skips the SMS check, preventing the crash.
    phone_number = getattr(website.user, 'phone_number', None) 
    
    # --- Message Construction ---
    subject = f"ALERT: Site {website.name} is {trigger_type}!"
    message_body = (
        f"The website {website.url} just changed status to {trigger_type} "
        f"on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}."
    )

    # --- Dispatch Logic (Uses your provided snippet) ---
    
    # 1. Email Dispatch
    # NOTE: Ensure your settings.py has EMAIL_ENABLED = True
    if settings.EMAIL_ENABLED and recipient_email:
        send_email_alert(
            recipient_email=recipient_email,
            subject=subject,
            message_body=message_body
        )
        
    # 2. SMS Dispatch
    # NOTE: Ensure your settings.py has SMS_ENABLED = True
    if settings.SMS_ENABLED and phone_number:
        send_twilio_sms(
            to_number=phone_number,
            message_body=message_body
        )