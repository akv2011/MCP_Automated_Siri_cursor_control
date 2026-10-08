#!/usr/bin/env python3
"""
Test script for Gemini integration with Pydantic validation
"""

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import ValidationError
from schemas import CursorAction, ActionType

# Load environment variables
load_dotenv()

# Configure Gemini API - New SDK needs explicit API key configuration
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")
client = genai.Client(api_key=api_key)
model_name = "gemini-2.5-flash"

def test_gemini_processing():
    """Test the Gemini processing function"""
    test_messages = [
        "Create a Python hello world script",
        "Open the app.py file", 
        "Search for the word 'flask' in my code",
        "Run python --version",
        "Make a new file called test.js with console.log('Hello')"
    ]
    
    for message in test_messages:
        print(f"\n🔍 Testing message: '{message}'")
        
        prompt = f"""
        You are an AI assistant that processes SMS messages to perform code actions in Cursor editor.
        
        The user sent: "{message}"
        
        Based on this message, determine what action should be performed in Cursor. You can:
        1. Create a new file
        2. Edit existing code
        3. Run code
        4. Search for code
        5. Open a specific file
        6. Execute terminal commands
        
        Respond with a JSON object containing:
        - action: the type of action to perform
        - command: the specific command or code to execute
        - description: a brief description of what will be done
        - file_path: if applicable, the file path to work with
        
        Example response:
        {{"action": "create_file", "command": "print('Hello World')", "description": "Creating a Python hello world script", "file_path": "hello.py"}}
        """
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for faster response
                )
            )
            print(f"📄 Raw response: {response.text}")
            
            # Try to parse as JSON and validate with Pydantic
            try:
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text[7:]  # Remove ```json
                if response_text.startswith('```'):
                    response_text = response_text[3:]   # Remove ```
                if response_text.endswith('```'):
                    response_text = response_text[:-3]  # Remove ```
                
                response_text = response_text.strip()
                
                # Parse raw JSON
                raw_data = json.loads(response_text)
                print(f"📄 Raw JSON: {json.dumps(raw_data, indent=2)}")
                
                # Validate with Pydantic
                action_data = CursorAction(**raw_data)
                print(f"✅ Validated action: {action_data.action}")
                print(f"📋 Description: {action_data.description}")
                print(f"⚙️  Command: {action_data.command}")
                if action_data.file_path:
                    print(f"📁 File path: {action_data.file_path}")
                    
            except ValidationError as e:
                print(f"❌ Pydantic validation error: {e}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                
        except Exception as e:
            print(f"❌ Gemini API error: {e}")

if __name__ == '__main__':
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please create a .env file with your Gemini API key")
    else:
        print("🚀 Starting Gemini integration test...")
        test_gemini_processing()
