import requests
import time
from datetime import datetime

# Define the acceptable threshold for a "SLOW" response (e.g., half a second)
RESPONSE_TIME_THRESHOLD = 0.5 # seconds

def check_website_health(url):
    """
    Pings a URL and returns its status, response time, and status code.
    """
    try:
        # Start the request, setting a reasonable timeout (e.g., 10 seconds)
        # Use a HEAD request (faster) if you only need the status code,
        # but GET is safer for full health checks. We'll use GET here.
        start_time = time.time()
        
        response = requests.get(url, timeout=10, allow_redirects=True)
        
        # Calculate the response time
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        status_code = response.status_code
        
        # --- Determine the Health Status ---
        if 200 <= status_code < 300:
            if elapsed_time > RESPONSE_TIME_THRESHOLD:
                health_status = "SLOW"
                color = "warning"
            else:
                health_status = "UP"
                color = "success"
        else:
            # 4xx or 5xx error codes
            health_status = "DOWN"
            color = "danger"

        return {
            "status": health_status,
            "response_time": round(elapsed_time, 3), # rounded to 3 decimal places
            "status_code": status_code,
            "checked_at": datetime.now().isoformat(),
            "color": color
        }

    except requests.exceptions.Timeout:
        return {
            "status": "DOWN",
            "response_time": -1, # Using -1 to indicate timeout
            "status_code": 408, # Request Timeout
            "checked_at": datetime.now().isoformat(),
            "color": "danger"
        }
    except requests.exceptions.RequestException:
        # Catch all other network/DNS errors (e.g., connection refused)
        return {
            "status": "DOWN",
            "response_time": -1,
            "status_code": 0, # Custom code for connection error
            "checked_at": datetime.now().isoformat(),
            "color": "danger"
        }


# --- HOW TO CHECK THE OUTPUT ---
if __name__ == "__main__":
    # Test a site that should be UP
    up_site = "https://www.google.com"
    print(f"Checking {up_site}...")
    result_up = check_website_health(up_site)
    print(result_up)
    
    print("-" * 20)

    # Test a site that is likely DOWN (or doesn't exist)
    down_site = "http://definitely-does-not-exist-12345.com" 
    print(f"Checking {down_site}...")
    result_down = check_website_health(down_site)
    print(result_down)