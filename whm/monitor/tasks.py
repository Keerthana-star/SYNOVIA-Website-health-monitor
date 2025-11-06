import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Website, CheckResult, AlertContact
import logging
from twilio.rest import Client
from django.core.mail import EmailMultiAlternatives 

logger = logging.getLogger(__name__)

# --- Alerting Functions ---

def send_email_alert(contact_value, website_name, status, message):
    if not settings.EMAIL_ENABLED:
        logger.info(f"Email alerting disabled. Skipping email to {contact_value} for {website_name}.")
        return

    subject = f"ALERT: {website_name} is {status}"
    text_content = f"""
    Website Health Monitor Alert!

    Website: {website_name}
    Status: {status}
    Time: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
    Details: {message}
    """
    html_content = f"""
    <html>
        <body style="font-family: sans-serif; padding: 20px; border: 1px solid #ddd;">
            <h2 style="color: {'#dc2626' if status == 'DOWN' else '#16a34a'};">
                Website Health Monitor Alert!
            </h2>
            <p><strong>Website:</strong> {website_name}</p>
            <p><strong>Status:</strong> <span style="font-weight: bold;">{status}</span></p>
            <p><strong>Time:</strong> {timezone.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
            <p><strong>Details:</strong> {message}</p>
        </body>
    </html>
    """

    try:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [contact_value])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info(f"Email alert sent successfully to {contact_value} for {website_name}.")
    except Exception as e:
        logger.error(f"Failed to send email alert to {contact_value} for {website_name}: {e}")

def send_sms_alert(contact_value, website_name, status, message):
    if not settings.SMS_ENABLED:
        logger.info(f"SMS alerting disabled. Skipping SMS to {contact_value} for {website_name}.")
        return

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        body = f"WHM ALERT: {website_name} is {status}. Details: {message[:100]}..."
        
        client.messages.create(
            to=contact_value,
            from_=settings.TWILIO_PHONE_NUMBER,
            body=body
        )
        logger.info(f"SMS alert sent successfully to {contact_value} for {website_name}.")
    except Exception as e:
        logger.error(f"Failed to send SMS alert to {contact_value} for {website_name}: {e}")


def trigger_alerts(website, new_status, message):
    """Triggers all active alerts for the given website."""
    contacts = AlertContact.objects.filter(websites=website, is_active=True).select_related('user')
    
    for contact in contacts:
        if contact.contact_type == 'EMAIL':
            send_email_alert(contact.value, website.name, new_status, message)
        elif contact.contact_type == 'SMS':
            send_sms_alert(contact.value, website.name, new_status, message)

# --- Core Task ---

@shared_task(bind=True)
def check_website(self, website_id):
    """Performs a single health check on a Website object."""
    try:
        website = Website.objects.get(pk=website_id)
    except Website.DoesNotExist:
        logger.error(f"Website with ID {website_id} not found.")
        return

    url = website.url
    method = website.http_method
    
    is_up = False
    status_code = 0
    response_time_ms = 0
    error_message = None
    
    try:
        start_time = timezone.now()
        response = requests.request(method, url, timeout=15, allow_redirects=True)
        end_time = timezone.now()
        response_time_ms = int((end_time - start_time).total_seconds() * 1000)
        status_code = response.status_code
        
        if 200 <= status_code < 400:
            is_up = True
            new_status = 'UP'
        else:
            is_up = False
            new_status = 'DOWN'
            error_message = f"HTTP Status Code {status_code}"
            
    except requests.exceptions.Timeout:
        status_code = 408 
        is_up = False
        new_status = 'DOWN'
        error_message = "Request timed out after 15 seconds."
        
    except requests.exceptions.RequestException as e:
        status_code = 0 
        is_up = False
        new_status = 'DOWN'
        error_message = str(e)
        
    # 1. Save the result
    CheckResult.objects.create(
        website=website,
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_up=is_up,
        error_message=error_message
    )

    # 2. Update Website Status and Last Checked time
    website.last_checked = timezone.now()
    
    # 3. Trigger Alert if status has changed to DOWN
    old_status = website.status
    if old_status != new_status:
        website.status = new_status
        if new_status == 'DOWN':
            logger.warning(f"Status change detected: {website.name} is now DOWN. Triggering alerts.")
            trigger_alerts(website, new_status, error_message or "Unknown Error")
        elif new_status == 'UP' and old_status != 'UNKNOWN':
            # Send recovery alert
            logger.info(f"Status change detected: {website.name} is now UP.")
            trigger_alerts(website, new_status, "Recovery: The website is back online.")
            
    website.save()
    
    logger.info(f"Checked {url}: Status={new_status}, Code={status_code}, Time={response_time_ms}ms")


@shared_task
def run_all_checks():
    """Celery Beat task to queue checks for all websites that are due."""
    now = timezone.now()
    websites = Website.objects.all()
    
    for website in websites:
        if website.last_checked:
            time_since_last_check = now - website.last_checked
            check_interval = timezone.timedelta(minutes=website.frequency)
            
            if time_since_last_check >= check_interval:
                check_website.delay(website.id)
                logger.info(f"Queued check for {website.name}")
        else:
            # Check immediately if never checked before
            check_website.delay(website.id)
            logger.info(f"Queued initial check for {website.name}")
            
    logger.info(f"Finished queuing checks for {websites.count()} websites.")