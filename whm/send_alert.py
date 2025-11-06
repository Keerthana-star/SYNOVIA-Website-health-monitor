import os
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# --- Configuration (Set these in your environment variables/config file) ---
# Example for Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_SMS_NUMBER = os.environ.get("TWILIO_SMS_NUMBER")
TWILIO_WA_NUMBER = os.environ.get("TWILIO_WA_NUMBER") # Needs to be configured for WhatsApp
USER_PHONE_NUMBER = os.environ.get("USER_PHONE_NUMBER") 

# Example for SendGrid
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
ALERT_SENDER_EMAIL = os.environ.get("ALERT_SENDER_EMAIL")
ALERT_RECIPIENT_EMAIL = os.environ.get("ALERT_RECIPIENT_EMAIL")