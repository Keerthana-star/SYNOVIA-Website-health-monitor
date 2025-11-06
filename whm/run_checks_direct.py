# run_checks_direct.py (MUST BE EXACTLY THIS)

import os
import django
import time
import logging

# Ensure this path is correct for your project settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monitor_project.settings')
django.setup() 
# This line sets up the environment and should run successfully

from monitor.tasks import check_website_health 

logger = logging.getLogger(__name__)

# Run the task every 60 seconds (or 10 for quick testing)
INTERVAL_SECONDS = 60

# --- THE CRITICAL LOOP ---
if __name__ == '__main__':
    print("--- Starting Direct Website Health Checker ---")
    print(f"Monitoring sites every {INTERVAL_SECONDS} seconds...")
    
    # This loop MUST run indefinitely
    while True:
        try:
            # 1. Execute your monitoring function
            check_website_health()
            
            print(f"Checks complete at {time.strftime('%H:%M:%S')}. Waiting {INTERVAL_SECONDS} seconds...")
            
            # 2. Wait for the defined interval
            time.sleep(INTERVAL_SECONDS)
        
        except Exception as e:
            import traceback
            # If an error happens inside the checker, print it and wait
            print(f"AN ERROR OCCURRED IN THE CHECKER: {e}")
            print(traceback.format_exc()) 
            time.sleep(5)
            
# The script should not reach the end.