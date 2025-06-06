# app.py

import threading
import time
import logging
from datetime import datetime, timezone, timedelta

import streamlit as st

# 1) Define a logging.Formatter subclass that forces timestamps into GMT+5:30
class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        # if no tz is provided, default to UTC
        self.tz = tz or timezone.utc

    def formatTime(self, record, datefmt=None):
        # Convert record.created (a POSIX timestamp) into the desired timezone
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            # Fallback to ISO if no datefmt is provided
            return dt.isoformat()

# 2) Set up the root logger to use our TZFormatter with GMT+5:30
#    You can also change StreamHandler() to FileHandler("mylog.log") if you
#    prefer writing to a file instead of stdout.
tz_india = timezone(timedelta(hours=5, minutes=30))
formatter = TZFormatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    tz=tz_india
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

root_logger = logging.getLogger()    # get the root logger
root_logger.setLevel(logging.INFO)
# Remove any existing handlers, then add ours
if root_logger.hasHandlers():
    root_logger.handlers.clear()
root_logger.addHandler(handler)

# 3) Define the actual "job" function that logs the current timestamp in GMT+5:30
def log_timestamp_job():
    now = datetime.now(tz_india)
    formatted = now.strftime("%Y-%m-%d %H:%M:%S %z")
    logging.info(f"Current timestamp (GMT+5:30): {formatted}")

# 4) Define a scheduler loop that calls log_timestamp_job() every 60 seconds
def scheduler_loop():
    # Optionally, wait until the next full minute to align exactly on :00
    # now = datetime.now(tz_india)
    # seconds_to_next_minute = 60 - now.second
    # time.sleep(seconds_to_next_minute)
    while True:
        log_timestamp_job()
        time.sleep(60)

# 5) Use Streamlit's @st.experimental_singleton to ensure the scheduler thread
#    is started exactly once (per process). Even if Streamlit re-runs the script
#    on each page interaction, this singleton will prevent multiple threads.
@st.experimental_singleton
def start_background_scheduler():
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()
    return True

# 6) Main Streamlit app
def main():
    # Kick off the scheduler thread as soon as the app loads
    start_background_scheduler()

    st.title("Streamlit Cron‐Style Logger")
    st.write(
        """
        This Streamlit app logs a timestamp **every minute** (in GMT+5:30) 
        to the console (or to a file, if you switch to FileHandler).  
        The background thread runs independently of any front‐end usage, 
        so timestamps will keep being recorded even if no one is viewing the page.
        """
    )
    st.markdown("---")
    st.markdown("**Check your terminal (or logfile) to see the timestamp entries.**")

if __name__ == "__main__":
    main()
