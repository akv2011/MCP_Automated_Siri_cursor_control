#!/usr/bin/env python3
"""
Twilio Configuration Diagnostic
"""

import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables - override system variables with .env file
load_dotenv(override=True)

# Get Twilio configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

print("Twilio Configuration Diagnostic")
print("=" * 40)
print(f"Account SID: {TWILIO_ACCOUNT_SID}")
print(f"From Number: {TWILIO_PHONE_NUMBER}")
print(f"Auth Token: {'*' * 20}{TWILIO_AUTH_TOKEN[-4:] if TWILIO_AUTH_TOKEN else 'None'}")

# Test Twilio connection
try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Get account info
    account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
    print(f"\nOK Account Status: {account.status}")
    print(f"OK Account Type: {account.type}")
    
    # List phone numbers
    print(f"\nAvailable Phone Numbers:")
    incoming_numbers = client.incoming_phone_numbers.list()
    for number in incoming_numbers:
        print(f"  - {number.phone_number} ({number.friendly_name})")
    
    print(f"\nTest SMS Send:")
    print(f"FROM: {TWILIO_PHONE_NUMBER}")
    print(f"TO: {os.getenv('OWNER_PHONE', '')}")
    
    if TWILIO_PHONE_NUMBER == os.getenv("OWNER_PHONE", ""):
        print("ERROR ERROR: FROM and TO numbers are the same!")
    else:
        print("OK Numbers are different - should work")
        
except Exception as e:
    print(f"ERROR Twilio Error: {e}")
