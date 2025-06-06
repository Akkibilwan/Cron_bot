# app.py

import threading
import time
import logging
from datetime import datetime, timezone, timedelta

import streamlit as st

# ─── 1) Logging setup ────────────────────────────────────────────────────────
class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        # Default to UTC if no tz is provided
        self.tz = tz or timezone.utc

    def formatTime(self, record, datefmt=None):
        # Convert the POSIX timestamp to the desired timezone
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# Timezone for GMT+5:30
tz_india = timezone(timedelta(hours=5, minutes=30))

formatter = TZFormatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    tz=tz_india
)

handler = logging.StreamHandler()  # switch to FileHandler("mylog.log") if you want a file
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# Clear any existing handlers (avoid duplicate logs)
if root_logger.hasHandlers():
    root_logger.handlers.clear()
root_logger.addHandler(handler)

# ─── 2) Cron‐style job function ───────────────────────────────────────────────
def log_timestamp_job():
    now = datetime.now(tz_india)
    formatted = now.strftime("%Y-%m-%d %H:%M:%S %z")
    logging.info(f"Current timestamp (GMT+5:30): {formatted}")

def scheduler_loop():
    # Uncomment to align to the top of each minute:
    # now = datetime.now(tz_india)
    # seconds_to_next_minute = 60 - now.second
    # time.sleep(seconds_to_next_minute)
    while True:
        log_timestamp_job()
        time.sleep(60)

# ─── 3) Ensure only one background thread per process ─────────────────────────
_scheduler_thread = None

def start_background_scheduler():
    global _scheduler_thread
    if _scheduler_thread is None:
        _scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        _scheduler_thread.start()

# ─── 4) Streamlit UI ─────────────────────────────────────────────────────────
def main():
    # Kick off the scheduler thread exactly once
    start_background_scheduler()

    st.title("Streamlit Cron‐Style Logger")
    st.write(
        """
        This app logs a timestamp **every minute** (GMT+5:30) to the console (or logfile).  
        A background thread runs independently of any front‐end usage, so you will see logs 
        even if no one is viewing the page.
        """
    )
    st.markdown("---")
    st.markdown("**Check your terminal (or logfile) to see the timestamp entries.**")

if __name__ == "__main__":
    main()
