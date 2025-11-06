# monitor_engine.py

import requests
import time
import json
import os
from datetime import datetime

# --- Configuration ---
# Flask server address where the API is running
API_BASE_URL = "http://127.0.0.1:5000/api" 
CHECK_INTERVAL_SECONDS = 30 # Check sites every 30 seconds
RESPONSE_TIME_THRESHOLD = 0.5 

# --- Alert Functions (Link to your real code from previous response) ---
def send_alert_email(site_url, status_code, message):
    # This function must contain your real SendGrid/Mailgun API calls
    print(f"[EMAIL MOCK] Alert for {site_url}: {message}") 

def send_alert_sms(site_url, status_code, message):
    # This function must contain your real Twilio SMS API calls
    print(f"[SMS MOCK] Alert for {site_url}: {message}") 

def check_single_site(url):
    """Pings a URL and returns its status data."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        elapsed_time = time.time() - start_time
        status_code = response.status_code
        
        if 200 <= status_code < 300:
            status = "SLOW" if elapsed_time > RESPONSE_TIME_THRESHOLD else "UP"
        else:
            status = "DOWN"

        return {
            "url": url,
            "status": status,
            "status_code": status_code,
            "response_time": elapsed_time
        }

    except requests.exceptions.Timeout:
        return {"url": url, "status": "DOWN", "status_code": 408, "response_time": -1}
    except requests.exceptions.RequestException:
        return {"url": url, "status": "DOWN", "status_code": 0, "response_time": -1}

# --- Main Monitoring Loop ---
def run_monitoring_engine():
    print("Monitoring Engine Started...")
    while True:
        try:
            # 1. Fetch all sites and their current status from the API
            response = requests.get(f"{API_BASE_URL}/websites")
            response.raise_for_status()
            sites = response.json()
            
            print(f"\n--- Checking {len(sites)} sites @ {datetime.now().strftime('%H:%M:%S')} ---")
            
            for site_data in sites:
                url = site_data['url']
                previous_status = site_data['status']
                
                # 2. Check the current status of the site
                current_result = check_single_site(url)
                current_status = current_result['status']
                
                print(f"[{current_status.upper()}] {url}")
                
                # 3. ALERT TRIGGER LOGIC
                alert_message = None
                
                # Site goes DOWN
                if current_status == "DOWN" and previous_status in ["UP", "SLOW", "UNKNOWN"]:
                    alert_message = f"Status changed from {previous_status} to DOWN."
                
                # Site RECOVERS
                elif current_status in ["UP", "SLOW"] and previous_status == "DOWN":
                    alert_message = f"Status changed to {current_status} (Recovery)."

                if alert_message:
                    # Trigger the actual alerts
                    send_alert_email(url, current_result['status_code'], alert_message)
                    send_alert_sms(url, current_result['status_code'], alert_message)
                
                # 4. Update status and history via API
                requests.post(f"{API_BASE_URL}/update_status", json=current_result)
                
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Could not connect to API or network error: {e}")
        except Exception as e:
            print(f"AN UNEXPECTED ERROR OCCURRED: {e}")
            
        time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    run_monitoring_engine()