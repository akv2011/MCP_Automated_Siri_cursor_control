#!/usr/bin/env python3
"""
SMS-Cursor MCP Bridge - Using FastMCP for reliable tool integration
"""

from typing import Any
from fastmcp import FastMCP
import logging
import os
import subprocess
import glob
import shlex
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables - override system variables
load_dotenv(override=True)

# Configure logging  
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sms-cursor-bridge")

# Project directory
PROJECT_DIR = os.getenv("PROJECT_DIR", os.getcwd())

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')


READ_ONLY = {"ls": None, "grep": None, "find": None, "git": {"status", "log", "diff", "show", "branch"}}
FIND_ACTIONS = {"-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprint0", "-fprintf", "-fls"}
GIT_BRANCH_FLAGS = {"-a", "-r", "-v", "-vv", "--all", "--remotes", "--list"}


def allowed_numbers() -> set[str]:
    return {n.strip() for n in os.getenv("ALLOWED_SENDERS", "").split(",") if n.strip()}


def checked_recipient(number: str) -> str:
    if number not in allowed_numbers():
        raise PermissionError(f"{number} is not in ALLOWED_SENDERS")
    return number


def parse_command(command: str) -> list[str]:
    """Split a command into argv and refuse anything that can write, delete or run other code."""
    argv = shlex.split(command)
    if not argv or argv[0] not in READ_ONLY:
        raise PermissionError(f"only {', '.join(sorted(READ_ONLY))} are allowed")
    if argv[0] == "git":
        if len(argv) < 2 or argv[1] not in READ_ONLY["git"]:
            raise PermissionError("git allows only status, log, diff, show and branch")
        if any(a.startswith("--output") or a.startswith("--ext-diff") for a in argv):
            raise PermissionError("git output redirection and external diff tools are not allowed")
        if argv[1] == "branch" and not set(argv[2:]) <= GIT_BRANCH_FLAGS:
            raise PermissionError("git branch is list-only")
    if argv[0] == "find" and FIND_ACTIONS & set(argv):
        raise PermissionError("find actions that run, delete or write files are not allowed")
    return argv

mcp = FastMCP("sms-cursor-bridge")

@mcp.tool()
async def sms_command(command: str) -> str:
    """Process SMS commands for Cursor automation.

    Args:
        command: The SMS command to process
    """
    logger.info(f"Processing SMS command: {command}")
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Just return the command for Cursor to handle naturally  
    return f"""📱 SMS Command received at {timestamp}: "{command}"

Please process this SMS command and create any requested files or perform the requested actions."""

@mcp.tool()
async def process_sms_request(sms_message: str) -> str:
    """Process SMS request and return instructions for Cursor to handle.

    Args:
        sms_message: The SMS message received from phone
    """
    logger.info(f"Processing SMS request: {sms_message}")
    
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Just return the SMS request for Cursor to process naturally
    return f"""📱 SMS Request received at {timestamp}:
"{sms_message}"

Please handle this request by creating the appropriate files or performing the requested actions. The SMS was sent to automate Cursor via SMS-to-Cursor bridge."""

@mcp.tool()
async def cursor_automation(action: str, target: str = "") -> str:
    """Perform automation actions in Cursor.

    Args:
        action: The action to perform (create, open, search, etc.)
        target: The target file or content
    """
    logger.info(f"Cursor automation: {action} on {target}")
    
    timestamp = datetime.now().strftime('%H%M%S')
    
    if action == "create":
        return f"✅ Created {target} via SMS automation at {timestamp}"
    elif action == "open":
        return f"✅ Opened {target} via SMS automation at {timestamp}"
    elif action == "search":
        return f"✅ Searched for {target} via SMS automation at {timestamp}"
    else:
        return f"✅ Performed {action} on {target} via SMS automation at {timestamp}"

@mcp.tool()
async def count_tests() -> str:
    """Count the number of test files in the codebase."""
    logger.info("Counting test files...")
    
    try:
        test_patterns = [
            os.path.join(PROJECT_DIR, "**", "test_*.py"),
            os.path.join(PROJECT_DIR, "**", "*_test.py"),
            os.path.join(PROJECT_DIR, "tests", "**", "*.py"),
            os.path.join(PROJECT_DIR, "**", "test*.py")
        ]
        
        test_files = []
        for pattern in test_patterns:
            test_files.extend(glob.glob(pattern, recursive=True))
        
        # Remove duplicates
        test_files = list(set(test_files))
        
        result = f"Test Analysis Complete:\n\n"
        result += f"Total test files found: {len(test_files)}\n\n"
        
        if test_files:
            result += "Test files:\n"
            for i, test_file in enumerate(test_files, 1):
                rel_path = os.path.relpath(test_file, PROJECT_DIR)
                result += f"{i}. {rel_path}\n"
        else:
            result += "No test files found in the codebase."
        
        return result
        
    except Exception as e:
        return f"Error counting tests: {str(e)}"

@mcp.tool()
async def find_large_files(min_lines: int = 1000) -> str:
    """Find files in the system over specified number of lines.
    
    Args:
        min_lines: Minimum number of lines (default: 1000)
    """
    logger.info(f"Finding files with more than {min_lines} lines...")
    
    try:
        large_files = []
        
        # Search for Python, JavaScript, and other code files
        file_patterns = [
            "**/*.py", "**/*.js", "**/*.ts", "**/*.java", 
            "**/*.cpp", "**/*.c", "**/*.cs", "**/*.php",
            "**/*.html", "**/*.css", "**/*.sql"
        ]
        
        for pattern in file_patterns:
            files = glob.glob(os.path.join(PROJECT_DIR, pattern), recursive=True)
            
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        line_count = sum(1 for _ in f)
                    
                    if line_count >= min_lines:
                        rel_path = os.path.relpath(file_path, PROJECT_DIR)
                        large_files.append((rel_path, line_count))
                        
                except Exception:
                    continue
        
        # Sort by line count (descending)
        large_files.sort(key=lambda x: x[1], reverse=True)
        
        result = f"Large Files Analysis (>{min_lines} lines):\n\n"
        result += f"Found {len(large_files)} large files:\n\n"
        
        for i, (file_path, line_count) in enumerate(large_files, 1):
            result += f"{i}. {file_path} ({line_count:,} lines)\n"
        
        if not large_files:
            result += f"No files found with more than {min_lines} lines."
        
        return result
        
    except Exception as e:
        return f"❌ Error finding large files: {str(e)}"

@mcp.tool()
async def analyze_codebase() -> str:
    """Analyze the current codebase structure and statistics."""
    logger.info("Analyzing codebase...")
    
    try:
        stats = {
            'total_files': 0,
            'python_files': 0,
            'javascript_files': 0,
            'total_lines': 0,
            'directories': 0
        }
        
        file_types = {}
        
        for root, dirs, files in os.walk(PROJECT_DIR):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', 'env']]
            
            stats['directories'] += len(dirs)
            
            for file in files:
                if file.startswith('.'):
                    continue
                    
                stats['total_files'] += 1
                
                # Count file types
                ext = os.path.splitext(file)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
                
                if ext == '.py':
                    stats['python_files'] += 1
                elif ext in ['.js', '.ts']:
                    stats['javascript_files'] += 1
                
                # Count lines
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        stats['total_lines'] += sum(1 for _ in f)
                except Exception:
                    continue
        
        result = f"📊 Codebase Analysis Complete:\n\n"
        result += f"Total files: {stats['total_files']:,}\n"
        result += f"Total directories: {stats['directories']:,}\n"
        result += f"Total lines of code: {stats['total_lines']:,}\n"
        result += f"Python files: {stats['python_files']:,}\n"
        result += f"JavaScript/TypeScript files: {stats['javascript_files']:,}\n\n"
        
        result += "File types breakdown:\n"
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_types[:10]:  # Top 10 file types
            result += f"{ext or '(no extension)'}: {count}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error analyzing codebase: {str(e)}"

@mcp.tool()
async def run_command(command: str) -> str:
    """Run a system command and return the output.
    
    Args:
        command: The command to execute
    """
    logger.info(f"Running command: {command}")
    
    try:
        argv = parse_command(command)
    except (PermissionError, ValueError) as e:
        return f"Command not allowed: {e}"

    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30, cwd=PROJECT_DIR)

        output = f"🖥️ Command: {command}\n"
        output += f"Exit code: {result.returncode}\n\n"
        
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        
        if result.stderr:
            output += f"Error:\n{result.stderr}\n"
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"❌ Command timed out: {command}"
    except Exception as e:
        return f"❌ Error running command: {str(e)}"

@mcp.tool()
async def send_sms_response(phone_number: str, message: str) -> str:
    """Send SMS response back to the user.
    
    Args:
        phone_number: The phone number to send SMS to
        message: The message content to send
    """
    logger.info(f"Sending SMS response to {phone_number}")
    
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            return "❌ Twilio credentials not configured"
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Truncate message if too long (SMS limit is 1600 chars)
        if len(message) > 1500:
            message = message[:1500] + "... [truncated]"
        
        message_instance = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=checked_recipient(phone_number)
        )
        
        return f"✅ SMS sent successfully to {phone_number}\nMessage SID: {message_instance.sid}"
        
    except Exception as e:
        return f"❌ Failed to send SMS: {str(e)}"

@mcp.tool()
async def send_completion_summary(phone_number: str, original_request: str, results: str, actions_performed: str = "") -> str:
    """Send a completion summary SMS with what was accomplished.
    
    Args:
        phone_number: The phone number to send SMS to
        original_request: The original SMS request
        results: The results/output from the operations
        actions_performed: Optional description of actions taken
    """
    logger.info(f"Sending completion summary to {phone_number}")
    
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            return "Twilio credentials not configured"
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create concise summary message
        timestamp = datetime.now().strftime('%H:%M')
        
        summary = f"SMS-to-Cursor Complete ({timestamp})\n\n"
        summary += f"Request: {original_request}\n\n"
        
        if actions_performed:
            summary += f"Action: {actions_performed}\n\n"
        
        summary += f"Results:\n{results}\n\n"
        summary += f"Automated via SMS bridge"
        
        # Truncate if too long (SMS limit is 1600 chars)
        if len(summary) > 1500:
            # Keep header and truncate results
            header = f"SMS-to-Cursor Complete ({timestamp})\nRequest: {original_request}\n\nResults:\n"
            max_results_length = 1400 - len(header) - 50
            truncated_results = results[:max_results_length] + "...[more]"
            summary = header + truncated_results + "\n\nAutomated via SMS"
        
        message_instance = client.messages.create(
            body=summary,
            from_=TWILIO_PHONE_NUMBER,
            to=checked_recipient(phone_number)
        )
        
        return f"Summary sent to {phone_number}, SID: {message_instance.sid}, Length: {len(summary)} chars"
        
    except Exception as e:
        return f"Failed to send summary: {str(e)}"

@mcp.tool()
async def send_summary_message(phone_number: str, message_type: str, content: str) -> str:
    """Send a simple summary message via SMS.
    
    Args:
        phone_number: The phone number to send SMS to
        message_type: Type of message (test_count, file_analysis, command_result, etc.)
        content: The content to send
    """
    logger.info(f"Sending {message_type} summary to {phone_number}")
    
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            return "Twilio credentials not configured"
        
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Create simple message based on type
        timestamp = datetime.now().strftime('%H:%M')
        
        if message_type == "test_count":
            message = f"Test Count ({timestamp}):\n{content}"
        elif message_type == "file_analysis":
            message = f"File Analysis ({timestamp}):\n{content}"
        elif message_type == "command_result":
            message = f"Command Result ({timestamp}):\n{content}"
        elif message_type == "codebase_stats":
            message = f"Codebase Stats ({timestamp}):\n{content}"
        else:
            message = f"SMS Result ({timestamp}):\n{content}"
        
        # Truncate if too long
        if len(message) > 1500:
            message = message[:1500] + "...[truncated]"
        
        message_instance = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=checked_recipient(phone_number)
        )
        
        return f"Message sent to {phone_number}, Type: {message_type}, SID: {message_instance.sid}"
        
    except Exception as e:
        return f"Failed to send message: {str(e)}"

@mcp.tool()
async def complete_sms_task(phone_number: str, original_request: str, task_type: str, min_lines: int = 300) -> str:
    """Complete an SMS task by running the appropriate analysis and sending results back.
    
    Args:
        phone_number: The phone number to send results to
        original_request: The original SMS request
        task_type: Type of task (count_tests, find_large_files, analyze_codebase, run_command)
        min_lines: Minimum lines for find_large_files (default: 300)
    """
    logger.info(f"Completing SMS task: {task_type} for {phone_number} with min_lines={min_lines}")
    
    try:
        results = ""
        actions = ""
        
        # Perform the requested task
        if task_type == "count_tests":
            results = await count_tests()
            actions = "Scanned codebase for test files"
            
        elif task_type == "find_large_files":
            results = await find_large_files(min_lines)  # Use the passed parameter
            actions = f"Analyzed file sizes across the codebase (>{min_lines} lines)"
            
        elif task_type == "analyze_codebase":
            results = await analyze_codebase()
            actions = "Performed complete codebase analysis"
            
        elif task_type.startswith("run_"):
            command = task_type.replace("run_", "").replace("_", " ")
            results = await run_command(command)
            actions = f"Executed command: {command}"
            
        else:
            results = f"Processed request: {original_request}"
            actions = "General SMS command processing"
        
        # Send completion summary
        summary_result = await send_completion_summary(
            phone_number, 
            original_request, 
            results, 
            actions
        )
        
        return f"Task completed and summary sent!\n\nTask: {task_type}\nActions: {actions}\nSMS Status: {summary_result}\n\nDetailed Results:\n{results}"
        
    except Exception as e:
        return f"❌ Failed to complete SMS task: {str(e)}"

if __name__ == "__main__":
    # Initialize and run the server (same as weather)
    logger.info("🚀 SMS-Cursor MCP Bridge starting...")
    mcp.run(transport='stdio')
