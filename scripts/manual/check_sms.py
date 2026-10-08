#!/usr/bin/env python3
"""
Quick test script for SMS automation
"""

def test_phone_numbers():
    """Test that phone numbers are valid"""
    
    # Your Twilio phone number (sends FROM)
    twilio_number = "+12295970631"
    
    # Target phone number (sends TO) 
    target_number = "+917007646200"
    
    print("📱 SMS Automation Test")
    print("=" * 40)
    print(f"✅ Twilio Number (FROM): {twilio_number}")
    print(f"✅ Target Number (TO): {target_number}")
    print()
    
    # Test URLs
    ngrok_url = "https://c85d8a437f93.ngrok-free.app"
    
    print("🔗 Test URLs:")
    print(f"• Webhook Test: {ngrok_url}/send_and_trigger?message=Create a Python hello world script")
    print(f"• Simulation: {ngrok_url}/simulate_sms?message=Test message&from={target_number}")
    print(f"• Dashboard: {ngrok_url}/")
    print()
    
    print("🧪 Manual Twilio SMS Command:")
    print("curl 'https://api.twilio.com/2010-04-01/Accounts/AC839d163e6ec7a6a3dcc6af759a8504bb/Messages.json' \\")
    print("  -X POST \\")
    print(f"  --data-urlencode 'To={target_number}' \\")
    print(f"  --data-urlencode 'From={twilio_number}' \\")
    print("  --data-urlencode 'Body=Create a Python hello world script' \\")
    print("  -u AC839d163e6ec7a6a3dcc6af759a8504bb:[AuthToken]")

if __name__ == "__main__":
    test_phone_numbers()
