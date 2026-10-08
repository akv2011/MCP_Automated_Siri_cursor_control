#!/usr/bin/env python3
"""
Startup Manager for SMS-to-Cursor Automation System
Helps start all required services in the correct order.
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("SMS-to-Cursor Automation System")
    print("=" * 50)
    print("Starting up all required services...")
    print()

def check_requirements():
    """Check if all required files and dependencies exist."""
    print("Checking requirements...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("ERROR .env file not found!")
        print("   Copy .env.example to .env and configure your API keys")
        return False
    
    # Check if required Python files exist
    required_files = [
        'src/app.py',
        'src/simple_ui_bridge.py',
        'working_sms_mcp_bridge.py'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"ERROR Required file missing: {file}")
            return False
    
    print("OK All requirements met!")
    return True

def start_service(name, command, wait_time=3):
    """Start a service and wait for it to initialize."""
    print(f"Starting {name}...")
    
    try:
        # Start the process
        process = subprocess.Popen(command, shell=True)
        time.sleep(wait_time)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"OK {name} started successfully (PID: {process.pid})")
            return process
        else:
            print(f"ERROR {name} failed to start")
            return None
    except Exception as e:
        print(f"ERROR Error starting {name}: {e}")
        return None

def check_service(name, url, timeout=5):
    """Check if a service is responding."""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"OK {name} is responding")
            return True
    except:
        pass
    
    print(f"WARNING {name} is not responding (may still be starting)")
    return False

def main():
    """Main startup function."""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    print("\nStartup Sequence:")
    print("1. Main SMS App (port 5000)")
    print("2. UI Automation Bridge (port 5002)")
    print("3. MCP Servers (optional)")
    print("4. Ngrok Tunnel (manual)")
    print()
    
    # Start main SMS app
    sms_app = start_service(
        "SMS App",
        "python src/app.py",
        wait_time=5
    )
    
    if not sms_app:
        print("ERROR Cannot continue without SMS App")
        sys.exit(1)
    
    # Start UI bridge
    ui_bridge = start_service(
        "UI Bridge", 
        "python src/simple_ui_bridge.py",
        wait_time=3
    )
    
    # Wait a bit more for services to fully initialize
    print("\nWaiting for services to initialize...")
    time.sleep(5)
    
    # Check service health
    print("\nHealth Check:")
    check_service("SMS App", "http://localhost:5000")
    check_service("UI Bridge", "http://localhost:5002")
    
    print("\nOK System Status:")
    print("SMS App: http://localhost:5000")
    print("UI Bridge: http://localhost:5002")
    print()
    print("Next Steps:")
    print("1. Start ngrok tunnel: ./ngrok http 5000")
    print("2. Configure Twilio webhook URL")
    print("3. Test by sending SMS or using dashboard")
    print()
    print("WARNING Keep this terminal open to monitor services")
    print("   Press Ctrl+C to stop all services")
    
    try:
        # Keep the script running to monitor services
        while True:
            time.sleep(30)
            # Check if services are still running
            if sms_app and sms_app.poll() is not None:
                print("ERROR SMS App stopped unexpectedly")
                break
                
            if ui_bridge and ui_bridge.poll() is not None:
                print("ERROR UI Bridge stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\nShutting down services...")
        
        if sms_app:
            sms_app.terminate()
            print("OK SMS App stopped")
            
        if ui_bridge:
            ui_bridge.terminate()
            print("OK UI Bridge stopped")
            
        print("System shutdown complete")

if __name__ == "__main__":
    main()
