#!/usr/bin/env python3
"""
Cron job script for Panchayat Seva Agent notifications.

This script is designed to run via scheduled cron jobs (e.g., Render Cron Jobs).
It scrapes new schemes, checks eligibility for all users, and sends WhatsApp notifications.

Usage:
    python cron_notify.py

Schedule (Render Cron Jobs):
    - Morning:  30 2 * * *  (8:00 AM IST)
    - Evening: 45 9 * * *   (3:15 PM IST)
"""

import sys
import os

# Ensure correct working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def main():
    """Main entry point for cron job"""
    print("[CRON] ============================================")
    print("[CRON] Panchayat Seva Agent - Notification Job")
    print(f"[CRON] Started at: {os.popen('date').read().strip()}")
    print("[CRON] ============================================")
    
    try:
        # Import after chdir to ensure correct module paths
        from notification_scheduler import trigger_scrape_and_notify_now
        
        print("[CRON] Running scrape and notify cycle...")
        result = trigger_scrape_and_notify_now()
        
        if result.get('success'):
            print(f"[CRON] Success: {result.get('users_notified', 0)} users notified")
            print(f"[CRON] New schemes found: {result.get('new_schemes', 0)}")
        else:
            print(f"[CRON] Job completed with issues: {result.get('error', 'Unknown error')}")
        
        print("[CRON] ============================================")
        print("[CRON] Job completed successfully")
        print("[CRON] ============================================")
        return 0
        
    except Exception as e:
        print(f"[CRON] ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("[CRON] ============================================")
        print("[CRON] Job FAILED")
        print("[CRON] ============================================")
        return 1

if __name__ == "__main__":
    sys.exit(main())
