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

print("🔍 Twilio Configuration Diagnostic")
print("=" * 40)
print(f"Account SID: {TWILIO_ACCOUNT_SID}")
print(f"From Number: {TWILIO_PHONE_NUMBER}")
print(f"Auth Token: {'*' * 20}{TWILIO_AUTH_TOKEN[-4:] if TWILIO_AUTH_TOKEN else 'None'}")

# Test Twilio connection
try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Get account info
    account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
    print(f"\n✅ Account Status: {account.status}")
    print(f"✅ Account Type: {account.type}")
    
    # List phone numbers
    print(f"\n📞 Available Phone Numbers:")
    incoming_numbers = client.incoming_phone_numbers.list()
    for number in incoming_numbers:
        print(f"  - {number.phone_number} ({number.friendly_name})")
    
    print(f"\n🧪 Test SMS Send:")
    print(f"FROM: {TWILIO_PHONE_NUMBER}")
    print(f"TO: +917007646200")
    
    if TWILIO_PHONE_NUMBER == "+917007646200":
        print("❌ ERROR: FROM and TO numbers are the same!")
    else:
        print("✅ Numbers are different - should work")
        
except Exception as e:
    print(f"❌ Twilio Error: {e}")
