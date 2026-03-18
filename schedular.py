#  scheduler.py  —  Runs tracker.py automatically every day
#  Usage:  python scheduler.py
#
#  Keep this running in a terminal (or background process).
#  It will check prices at the time you set below, every day.

import schedule
import time
from datetime import datetime
from tracker import run_tracker

# ---- Set your preferred daily check time here ----
RUN_AT = "09:00"   # 24-hour format — change to whatever you like
# --------------------------------------------------

def job():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Scheduled run starting...")
    run_tracker()

# Schedule the daily job
schedule.every().day.at(RUN_AT).do(job)

print(f"✅ Scheduler started. Tracker will run daily at {RUN_AT}.")
print(f"   Next run: {schedule.next_run()}")
print("   Press Ctrl+C to stop.\n")

# Also run immediately on startup so you don't wait till tomorrow
print("Running once now on startup...")
run_tracker()

# Keep the script alive, checking every minute if it's time to run
while True:
    schedule.run_pending()
    time.sleep(60)