#!/usr/bin/env python3
"""
Run script for Task Automator project
"""

import os
import subprocess
import sys
import time
import signal
import threading

processes = []

def signal_handler(signum, frame):
    print("\nShutting down all services...")
    for process in processes:
        if process and process.poll() is None:
            process.terminate()
    sys.exit(0)

def run_service(command, cwd=None, name="Service"):
    def run():
        try:
            print(f"Starting {name}...")
            process = subprocess.Popen(command, shell=True, cwd=cwd)
            processes.append(process)
            process.wait()
        except Exception as e:
            print(f"Error running {name}: {e}")
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def main():
    print("Task Automator - Starting all services...")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start Python backend
    python_backend_thread = run_service(
        "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload",
        name="Python Backend"
    )
    
    time.sleep(3)
    
    # Start dashboard backend
    dashboard_backend_thread = run_service(
        "npm start",
        cwd="dashboard/backend",
        name="Dashboard Backend"
    )
    
    time.sleep(3)
    
    # Start dashboard frontend
    dashboard_frontend_thread = run_service(
        "npm run dev",
        cwd="dashboard/frontend",
        name="Dashboard Frontend"
    )
    
    print("\nAll services started!")
    print("Dashboard: http://localhost:5173")
    print("API: http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main() 