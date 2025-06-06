# app.py

import threading
import time
import logging
from datetime import datetime, timezone, timedelta
import os

import streamlit as st

# ─── 1) Logging setup (write to a file) ───────────────────────────────────────
class TZFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, tz=None):
        super().__init__(fmt=fmt, datefmt=datefmt)
        self.tz = tz or timezone.utc

    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, self.tz)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.isoformat()

# Use GMT+5:30
tz_india = timezone(timedelta(hours=5, minutes=30))

formatter = TZFormatter(
    fmt="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %z",
    tz=tz_india
)

# Ensure “app.log” exists in the current working directory
LOG_PATH = os.path.join(os.getcwd(), "app.log")
if not os.path.exists(LOG_PATH):
    open(LOG_PATH, "a").close()

file_handler = logging.FileHandler(LOG_PATH)
file_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
if root_logger.hasHandlers():
    root_logger.handlers.clear()
root_logger.addHandler(file_handler)

# ─── 2) The cron‐style job (runs every 60 seconds) ─────────────────────────────
def log_timestamp_job():
    now = datetime.now(tz_india)
    formatted = now.strftime("%Y-%m-%d %H:%M:%S %z")
    logging.info(f"Current date & time: {formatted}")

def scheduler_loop():
    while True:
        log_timestamp_job()
        time.sleep(60)

# ─── 3) Start exactly one background thread per process ───────────────────────
_scheduler_thread = None

def start_cron_thread():
    global _scheduler_thread
    if _scheduler_thread is None:
        _scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        _scheduler_thread.start()

# ─── 4) Helper to read the last N lines from the log file ─────────────────────
def tail(file_path, n=10):
    """Return the last n lines from file_path."""
    try:
        with open(file_path, "rb") as f:
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
    # Kick off the cron thread (only once)
    start_cron_thread()

    st.title("Streamlit Cron-Style Logger")
    st.write(
        """
        A background thread is writing the current date & time (in GMT+5:30) 
        to `app.log` every minute. Below you’ll see the most recent entries.
        """
    )
    st.markdown("---")

    st.subheader("📄 Recent Log Entries (last 10 lines)")
    lines = tail(LOG_PATH, n=10)
    st.code("\n".join(lines), language=None)

    st.markdown("---")
    st.write(
        "Every 60 seconds the app adds a new timestamp to `app.log`. "
        "Refresh this page whenever you want to see the latest entries."
    )

if __name__ == "__main__":
    main()
