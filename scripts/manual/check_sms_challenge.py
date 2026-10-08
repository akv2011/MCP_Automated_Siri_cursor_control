#!/usr/bin/env python3
"""
Test script for SMS Challenge - Simulates the complete workflow
"""

import requests
import json
from datetime import datetime

def test_sms_challenge():
    """Test the complete SMS challenge workflow"""
    
    print("🧪 Testing SMS Challenge Workflow\n")
    
    # Test scenarios
    test_cases = [
        {
            "name": "Count Tests",
            "sms": "Count the number of tests we have",
            "expected_tools": ["count_tests", "send_sms_response"]
        },
        {
            "name": "Find Large Files",
            "sms": "Find files in my system over 1000 lines and list them",
            "expected_tools": ["find_large_files", "send_sms_response"]
        },
        {
            "name": "Analyze Codebase",
            "sms": "Analyze my codebase and tell me the statistics",
            "expected_tools": ["analyze_codebase", "send_sms_response"]
        },
        {
            "name": "Git Status",
            "sms": "Run git status command and send me the output",
            "expected_tools": ["run_command", "send_sms_response"]
        }
    ]
    
    # Test URL (your SMS webhook)
    webhook_url = "http://localhost:5000/sms"
    
    print("🔗 Testing SMS webhook endpoint...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📱 Test {i}: {test_case['name']}")
        print(f"SMS: '{test_case['sms']}'")
        
        # Simulate SMS webhook
        data = {
            'Body': test_case['sms'],
            'From': '+1234567890'  # Test phone number
        }
        
        try:
            response = requests.post(webhook_url, data=data, timeout=10)
            print(f"✅ Webhook response: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ SMS processed successfully")
            else:
                print(f"❌ Webhook failed: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ SMS webhook not running on {webhook_url}")
            print("   Start it with: cd src && python app.py")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📋 Manual Testing Steps:")
    print(f"1. Ensure SMS server is running: http://localhost:5000")
    print(f"2. Ensure MCP tools are loaded in Cursor")
    print(f"3. Send real SMS to your Twilio number")
    print(f"4. Check that response is sent back via SMS")

if __name__ == "__main__":
    test_sms_challenge()
