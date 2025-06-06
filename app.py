# app.py

import threading
import time
import logging
from datetime import datetime, timezone, timedelta
import os

import streamlit as st

# ─── 1) Logging setup (write to file instead of console) ─────────────────────
class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = tz or timezone.utc

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# Timezone GMT+5:30
tz_india = timezone(timedelta(hours=5, minutes=30))

formatter = TZFormatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    tz=tz_india
)

# Ensure the log directory/file exists
LOG_PATH = os.path.join(os.getcwd(), "app.log")
# Create file if it doesn't exist
if not os.path.exists(LOG_PATH):
    open(LOG_PATH, "a").close()

file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# Clear any existing handlers and add our file handler
if root_logger.hasHandlers():
    root_logger.handlers.clear()
root_logger.addHandler(file_handler)

# ─── 2) Cron‐style job function ───────────────────────────────────────────────
def log_timestamp_job():
    now = datetime.now(tz_india)
    formatted = now.strftime("%Y-%m-%d %H:%M:%S %z")
    logging.info(f"Current timestamp (GMT+5:30): {formatted}")

def scheduler_loop():
    # To align exactly at :00 seconds, uncomment below:
    # now = datetime.now(tz_india)
    # seconds_to_next_minute = 60 - now.second
    # time.sleep(seconds_to_next_minute)
    while True:
        log_timestamp_job()
        time.sleep(60)

# ─── 3) Only one background thread per process ────────────────────────────────
_scheduler_thread = None

def start_background_scheduler():
    global _scheduler_thread
    if _scheduler_thread is None:
        _scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        _scheduler_thread.start()

# ─── 4) Helper: read last N lines from the log file ───────────────────────────
def tail(file_path, n=10):
    """Return the last n lines from file_path."""
    try:
        with open(file_path, "rb") as f:
            # Seek to end and read backwards until we have enough lines
            f.seek(0, os.SEEK_END)
            buffer = bytearray()
            pointer_location = f.tell()
            lines_found = 0

            while pointer_location >= 0 and lines_found < n:
                f.seek(pointer_location)
                byte = f.read(1)
                if byte == b"\n" and buffer:
                    lines_found += 1
                    if lines_found == n:
                        break
                buffer.extend(byte)
                pointer_location -= 1

            buffer.reverse()
            last_lines = buffer.decode(errors="replace").splitlines()[-n:]
            return last_lines
    except Exception:
        return ["Unable to read log file."]

# ─── 5) Streamlit UI ─────────────────────────────────────────────────────────
def main():
    # Start the background thread (only once)
    start_background_scheduler()

    st.title("Streamlit Cron‐Style Logger (with In‐App Logs)")
    st.write(
        """
        This app writes a timestamp **every minute** (GMT+5:30) into `app.log` 
        in the working directory. You can see recent entries below.
        """
    )
    st.markdown("---")

    # Optionally auto-refresh every 60 seconds:
    # st.experimental_rerun()  # remove comment if you want a hard refresh each minute

    st.subheader("📄 Recent Log Entries (last 10 lines)")
    lines = tail(LOG_PATH, n=10)
    st.code("\n".join(lines), language=None)

    st.markdown("---")
    st.write(
        "Logs are stored in the file `app.log` in this app’s directory. "
        "If you need to download it, you can go to the Streamlit Cloud file browser "
        "or mount the storage and fetch it directly."
    )

if __name__ == "__main__":
    main()
