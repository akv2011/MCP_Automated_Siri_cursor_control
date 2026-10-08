"""
Pydantic schemas for SMS-to-Cursor automation
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum

class ActionType(str, Enum):
    """Valid action types for Cursor commands"""
    CREATE_FILE = "create_file"
    EDIT_FILE = "edit_file"
    RUN_CODE = "run_code"
    SEARCH_CODE = "search_code"
    OPEN_FILE = "open_file"
    ERROR = "error"

class CursorAction(BaseModel):
    """Schema for Cursor action responses from Gemini"""
    action: ActionType = Field(description="The type of action to perform")
    command: Optional[str] = Field(None, description="The specific command or code to execute")
    description: str = Field(description="A brief description of what will be done")
    file_path: Optional[str] = Field(None, description="File path if applicable")
    
    class Config:
        use_enum_values = True

class SMSResponse(BaseModel):
    """Schema for SMS response messages"""
    message: str = Field(description="The SMS message content")
    success: bool = Field(description="Whether the operation was successful")
    action_performed: Optional[str] = Field(None, description="Description of action performed")
    
    def to_sms_format(self) -> str:
        """Convert to SMS-friendly format"""
        if self.success:
            return f"OK {self.message}"
        else:
            return f"ERROR {self.message}"
