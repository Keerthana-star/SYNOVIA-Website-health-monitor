import requests
from datetime import datetime
from django.utils import timezone
from .models import MonitoredWebsite, AlertLog
from celery import shared_task
from django.core.mail import send_mail
from twilio.rest import Client # Needs pip install twilio

# --- Configuration (Move to settings.py for production) ---
# Simulating latency threshold (e.g., if response is over 500ms, mark as SLOW)
LATENCY_THRESHOLD_MS = 500 

# Twilio setup (replace these with your actual Twilio details)
TWILIO_ACCOUNT_SID = 'ACxxxxxxxxxxxxxxxxxxxxxxx' 
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+15017122661' # Your Twilio phone number

# --- HELPER FUNCTIONS ---

def send_sms_alert(phone_number, message):
    """Sends an SMS alert via Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Note: WhatsApp alerts use the same API endpoint but with a different 'from_' number format
        client.messages.create(
            to=phone_number,
            from_=TWILIO_PHONE_NUMBER,
            body=message
        )
        return True
    except Exception as e:
        print(f"Twilio SMS/WhatsApp Error: {e}")
        return False

def send_email_alert(recipient_list, subject, message):
    """Sends an email alert using Django's mail function."""
    try:
        # Requires EMAIL_BACKEND and other settings to be configured in settings.py
        send_mail(
            subject,
            message,
            'noreply@yourmonitor.com', # Use a valid sending email configured in settings
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email Alert Error: {e}")
        return False

def trigger_alerts(website, new_status, latency):
    """Sends alerts and logs the event for a status change."""
    
    # 1. Log the Alert (required for historical tracking)
    AlertLog.objects.create(
        website=website,
        old_status=website.status,
        new_status=new_status,
        alert_sent=True,
        message=f"Status changed from {website.status} to {new_status}. Latency: {latency or 'N/A'}"
    )

    # 2. Compose Alert Message
    status_change_msg = f"CRITICAL: {website.name} ({website.url}) status changed to {new_status}!"
    if new_status == 'UP':
         status_change_msg = f"RECOVERY: {website.name} ({website.url}) is back UP. Latency: {latency:.2f}ms."
         
    # 3. Send Email Alerts
    email_recipients = [e.strip() for e in website.alert_emails.split(',') if e.strip()]
    if email_recipients:
        send_email_alert(email_recipients, f"Monitor Alert: {new_status} for {website.name}", status_change_msg)

    # 4. Send SMS/WhatsApp Alerts
    phone_recipients = [p.strip() for p in website.alert_phones.split(',') if p.strip()]
    if phone_recipients:
        for phone in phone_recipients:
            send_sms_alert(phone, status_change_msg)


@shared_task
def check_website_health():
    """Celery task to run health checks on all monitored websites."""
    
    # Get all websites that are due for a check
    due_websites = MonitoredWebsite.objects.filter(
        # Check if last_check is null OR if enough time has passed since the last check
        models.Q(last_check__isnull=True) | 
        models.Q(last_check__lt=timezone.now() - timedelta(seconds=models.F('interval')))
    )
    
    for website in due_websites:
        old_status = website.status
        new_status = 'UNKNOWN'
        latency = None
        
        try:
            # Measure request time
            start_time = timezone.now()
            response = requests.get(website.url, timeout=10) # 10 second timeout
            end_time = timezone.now()
            
            # Calculate latency in milliseconds
            latency = (end_time - start_time).total_seconds() * 1000
            
            # Determine new status
            if response.status_code >= 200 and response.status_code < 400:
                if latency > LATENCY_THRESHOLD_MS:
                    new_status = 'SLOW'
                else:
                    new_status = 'UP'
            else:
                new_status = 'DOWN' # Treat any non-2xx/3xx as down

        except requests.exceptions.RequestException:
            new_status = 'DOWN'
            latency = None
        
        # 5. Update the Website record in the database
        website.status = new_status
        website.last_check = timezone.now()
        website.last_latency_ms = latency
        website.save()
        
        # 6. Trigger Alerts if Status Changed (DOWN/SLOW is critical, UP is recovery)
        if new_status != old_status:
            trigger_alerts(website, new_status, latency)


# Remember to configure Celery Beat to run this task every minute!
# E.g., CELERY_BEAT_SCHEDULE = {'check-health': {'task': 'monitor_project.tasks.check_website_health', 'schedule': crontab(minute='*')}}
