# app.py

import threading
import time
from datetime import datetime

import streamlit as st

# ─── 1) Define the “cron” job that prints the current date & time ─────────────
def cron_job():
    while True:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Current date & time: {now}")
        time.sleep(60)  # wait 60 seconds before printing again

# ─── 2) Ensure we only start one background thread per Streamlit process ────────
_thread_started = False

def start_cron_thread():
    global _thread_started
    if not _thread_started:
        thread = threading.Thread(target=cron_job, daemon=True)
        thread.start()
        _thread_started = True

# ─── 3) Streamlit UI ─────────────────────────────────────────────────────────
def main():
    # Kick off the background thread exactly once
    start_cron_thread()

    st.title("Simple Streamlit Cron")
    st.write(
        """
        A background thread is running and will print the current date & time 
        to the console every minute.  
        Check your terminal/console output to see the timestamps.
        """
    )

if __name__ == "__main__":
    main()
